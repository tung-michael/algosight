import json
import requests
from pymongo import MongoClient
import time
import logging

# For data collection
API_URL = 'https://mainnet-idx.algonode.cloud'
BLOCK_ENDPOINT = '/v2/blocks/'
BATCH_SIZE = 1000 # number of blocks fetched and processed in a batch

# For data preprocessing
TX_FIELDS = [
  "id", "tx-type", "sender", "fee",
  "confirmed-round", "group", "inner-txns", "round-time"
]
APPL_TX_FIELDS =[
  "accounts", "application-id", "foreign-apps", "foreign-assets"
]
PAY_TX_FIELDS =[
  "accounts", "application-id", "foreign-apps", "foreign-assets"
]


# For databases interaction
PG_CONFIG = 'postgres/setup/database.ini'
PG_LOG = "logs/pg_etl/etl.log"

MONGO_CONFIG = ''
MONGO_LOG = "logs/mongo_ingestion/ingestion.log"
MONGO_DB = {
  "host": "localhost",
  "port": 27017,
  "database": "defi_mock_db",
  "collection": "staging_transactions"
  # "collection": "transactions"
}


############## Data collection, pre-processing and ingestion (MongoDB) ###################

# Collect raw block data from AlgoNode API
def fetch_blocks(start: int, end: int) -> list:
  data = []
  for block_nr in range(start, end+1):
    for attempt in range(3):  # Retry up to 3 times
      response = requests.get(API_URL+BLOCK_ENDPOINT+f"{block_nr}")
      if response.status_code == 200:
        try:
          block = response.json()
          data.append(block)
          break
        except json.JSONDecodeError:
          logging.error(f"Failed to decode JSON response for block {block_nr} on attempt {attempt+1}: {response.text}")
          time.sleep(1)  # Sleep for 1 second before retrying
      else:
        logging.error(f"Failed to fetch block {block_nr} on attempt {attempt+1}: {response.status_code}")
        time.sleep(1)  # Sleep for 1 second before retrying
    else:
        logging.error(f"Failed to fetch block {block_nr} after 3 attempts.")
  return data

# Pre-process raw data
def filter_tx_data(transaction: dict) -> dict:
  filtered_tx = {}
  match transaction["tx-type"]:
    case "appl":
      filtered_tx["application-transaction"] = {
        field: transaction["application-transaction"][field]
          for field in APPL_TX_FIELDS
            if field in transaction["application-transaction"]
      }
    case "axfer":
      filtered_tx["asset-transfer-transaction"] = {}
      for key, value in transaction["asset-transfer-transaction"].items():
        if isinstance(value, int) and value > (2**63 - 1):
          value = str(value)
        filtered_tx["asset-transfer-transaction"][key] = value
    case "pay":
      filtered_tx["payment-transaction"] = {}
      for key, value in transaction["payment-transaction"].items():
        if isinstance(value, int) and value > (2**63 - 1):
          value = str(value)
        filtered_tx["payment-transaction"][key] = value
  for field in TX_FIELDS:
    if field in transaction.keys():
      if field == "inner-txns":
        filtered_tx["inner-txns"] = []
        for tx in transaction["inner-txns"]:
          filtered_tx["inner-txns"].append(filter_tx_data(transaction=tx))
      else:
        filtered_tx[field] = transaction[field]
    else:
      filtered_tx[field] = "N/A"
  return filtered_tx

# Collection, preprocess and ingestion to MongoDB
def collect_and_ingest(start: int, end: int, db_info: dict):
  # setup logging
  logging.basicConfig(
    filename=MONGO_LOG,
    filemode='a',
    format='%(asctime)s.%(msecs)d %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
  )
  logging.info("STARTING PROCESS...")
  # open connection to database
  # [TODO] change to read value from db_info
  mongo_client = MongoClient("localhost", 27017)
  mock_db = mongo_client['defi_mock_db']
  tx_collection = mock_db['staging_transactions']

  # crawl and load data to database
  while start < end+1:
    # collecting data in batch
    last = min (start+BATCH_SIZE-1, end) # last block in a batch
    raw_blocks = fetch_blocks(start=start, end=last)

    # preprocessing
    txns = []
    for block in raw_blocks:
      for tx in block['transactions']:
        txns.append(filter_tx_data(transaction=tx))

    # data ingestion and logging
    tx_collection.insert_many(txns)
    log_message = f"processing blocks_{start}_{last}"
    logging.info(log_message)

    # setup / cleanup parameters for next batch
    start = last+1
    txns.clear()
    raw_blocks.clear()
    del txns
    del raw_blocks

  # close connection to database
  logging.info("ENDING PROCESS...")
  mongo_client.close()


################# Prepare data for PostgreSQL database #########################

from datetime import datetime as dt
import csv

# Aggregated data derive from data in MongoDB. To be saved as csv files.
APP_CALLS_COLS = ["app_id", "round_time", "related_tx", "inner_tx_level"]
ASSET_TRANSFER_TXNS_COLS = [
  "asset_id",
  "amount",
  "round_time", "related_tx","inner_tx_level"
  ]

app_usage =[]
asset_usage = []

def convert_datetime(timestamp: int):
  dt_object = dt.fromtimestamp(timestamp)
  converted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
  return converted_time

# create an entry in either appl_usage or asset_usage for each transaction of that type
def generate_postgre_data(transaction: dict, level: int=0, parent_id: int=None):
  related_tx = transaction['id'] if parent_id==None else parent_id
  match transaction['tx-type']:
    case 'appl':
      app_usage.append([
        transaction['application-transaction']['application-id'],
        convert_datetime(transaction['round-time']),
        related_tx,
        level
      ])
    case 'axfer':
      asset_usage.append([
        transaction['asset-transfer-transaction']['asset-id'],
        int(transaction['asset-transfer-transaction']['amount']),
        convert_datetime(transaction['round-time']),
        related_tx,
        level
      ])
  if transaction['inner-txns'] != "N/A":
    for tx in transaction['inner-txns']:
      generate_postgre_data(transaction=tx, level=level+1, parent_id=related_tx)

# Get Access Info to PostgreSQL Database
import configparser
import psycopg2

def pg_parameters_extract (filename: str) -> dict:
  config = configparser.ConfigParser()
  config.read(filename)
  pg_params = {}
  if config.has_section(section='postgresql'):
    config_pg = config['postgresql']
    try:
      pg_params["dbname"] = config_pg["dbname"]
      pg_params["user"] = config_pg["user"]
      pg_params["password"] = config_pg["password"]
      pg_params["host"] = config_pg["host"]
      pg_params["port"] = config_pg["port"]
    except KeyError as e:
      print(e)
  else:
    raise ValueError(f'Section postgresql not found in the {filename} file.')
  return pg_params


################# ETL pipeline from MongoDB to PostgreSQL database #########################

ETL_BATCH_SIZE = 50000
from io import StringIO

def batch_insert_to_pg(
  table_name: str,
  col_names: list,
  data: list,
  pg_connection
  ):
  try:
    entries = len(data)
    # Create an in-memory file object and write on it
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerows(data) # After this step, buffer cursor is at the end of the "file"

    # Move the buffer cursor back to the start of the "file"
    buffer.seek(0)

    # Load data from buffer to Postgres
    cursor = pg_connection.cursor()
    cursor.copy_from(file=buffer, table=table_name, columns=col_names, sep=',')
    pg_connection.commit()
    logging.info(f"Inserted {entries} new entries to {table_name}")
  except Exception as e:
    logging.error(f"{e}")
    pg_connection.rollback()

  finally:
    buffer.close()


def etl_mongo_to_postgres():

  # setup log
  logging.basicConfig(
    filename=PG_LOG,
    filemode='a',
    format='%(asctime)s.%(msecs)d %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
  )
  # access Postgres
  pg_params = pg_parameters_extract(PG_CONFIG)
  conn = psycopg2.connect(
      dbname=pg_params["dbname"],
      user=pg_params["user"],
      password=pg_params["password"],
      host=pg_params["host"],
      port=pg_params["port"]
  )

  # access Mongo
  mongo_client = MongoClient(MONGO_DB["host"], MONGO_DB["port"])
  mock_db = mongo_client[MONGO_DB["database"]]
  tx_collection = mock_db[MONGO_DB["collection"]]

  # ETL run in batch
  total_entries = tx_collection.count_documents({})
  logging.info("STARTING ETL PIPELINE...")
  logging.info(f"Total: {total_entries} documents")


  for start_docs in range(0,total_entries, ETL_BATCH_SIZE):
    # Extract a batch of transactions
    mongo_txns = list(tx_collection.find({}).skip(start_docs).limit(ETL_BATCH_SIZE))
    log_message = f"Processing documents {start_docs+1} to {start_docs+len(mongo_txns)} of {total_entries} documents"
    logging.info(log_message)

    # Transformation
    for tx in mongo_txns:
      generate_postgre_data(transaction=tx)

    # Load in batch
    batch_insert_to_pg(
      table_name="app_calls",
      col_names=APP_CALLS_COLS,
      data=app_usage,
      pg_connection=conn
      )

    batch_insert_to_pg(
      table_name="asset_transfer_txns",
      col_names=ASSET_TRANSFER_TXNS_COLS,
      data=asset_usage,
      pg_connection=conn
      )

    # reset for next batch
    app_usage.clear()
    asset_usage.clear()

  logging.info("ETL COMPLETED.")
  conn.close()


####################### Extract dataset metadata #######################################
def get_meta_data(dataset: str = "1 day data"):
  with open('data/meta_data.json','r') as f:
    meta_data = json.load(f)[dataset]
  return meta_data


if __name__ == '__main__':

  # # Data collection, pre-processing and ingestion (Mongo)
  # meta_data = get_meta_data(dataset="1 month data")
  # start_block = meta_data["start block"]
  # end_block = meta_data["end block"]

  # collect_and_ingest(start=start_block, end=end_block, db_info={})

  # Run ETL pipeline
  etl_mongo_to_postgres()
