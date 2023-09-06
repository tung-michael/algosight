# For setting up and populating data base
import json
import requests
from pymongo import MongoClient
import time

API_URL = 'https://mainnet-idx.algonode.cloud'
BLOCK_ENDPOINT = '/v2/blocks/'
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

BATCH_SIZE = 1000 # number of blocks fetched and processed in a batch
DATA_DIR = "data/mongo/staging/"

PG_CONFIG = 'postgres_config/database.ini'
MONG_DB = {
  "host": "localhost",
  "port": 27017,
  "database": "defi_mock_db",
  "collection": "transactions"
}

############## Data collection and pre-processing JSON files ###################

# collect raw data

# new implementation of fetch_blocks
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

# old implementation of fetch_blocks
def fetch_blocks_old(start: int, end: int) -> list:
  data = []
  for block_nr in range(start, end+1):
    block = requests.get(API_URL+BLOCK_ENDPOINT+f"{block_nr}").json()
    data.append(block)
  return data

# pre-process raw data -> filtered data(JSON)
def data_filtering(transaction: dict) -> dict:
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
          filtered_tx["inner-txns"].append(data_filtering(transaction=tx))
      else:
        filtered_tx[field] = transaction[field]
    else:
      filtered_tx[field] = "N/A"
  return filtered_tx


def crawl_data(start: int, end: int):
  while start < end+1:
    # collecting data in batch
    last = min (start+BATCH_SIZE-1, end) # last block in a batch
    data = fetch_blocks(start=start, end=last)

    # preprocessing
    txns = []
    for block in data:
      for tx in block['transactions']:
          txns.append(data_filtering(transaction=tx))
    file_name = f"blocks_{start}_{last}"

    # save filtered data as JSON file
    with open(f'{DATA_DIR}{file_name}.json', 'w', encoding='utf-8') as f:
      json.dump(txns, f, ensure_ascii=False, indent=4)

    # setup / cleanup parameters for next batch
    start = last+1
    txns.clear()
    data.clear()
    del txns
    del data

################# No intermediate saved data file #########################
import logging
MONGO_LOG = "data/mongo/data_ingestion.log"

def crawl_and_ingestion(start: int, end: int, db_info: dict):
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
        txns.append(data_filtering(transaction=tx))

    # data ingestion and logging
    tx_collection.insert_many(txns)
    batch_name = f"blocks_{start}_{last}"
    log_message = f"{batch_name}"
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
################# Load data to Mongo #########################

def mongo_ingestion(
    collection,
    data_dir: str = DATA_DIR
  ):
  for filename in os.listdir(data_dir):
    if filename.endswith(".json"):
      file_path = os.path.join(data_dir, filename)
      with open(file_path) as file:
        data = json.load(file)
        collection.insert_many(data)

################# Prepare data for PostgreSQL database #########################

from datetime import datetime as dt
import csv

# Aggregated data derive from data in MongoDB. To be saved as csv files.
appl_usage = [["app_id", "round_time", "related_tx", "inner_tx_level"]]
asset_usage = [
  [
    "asset_id",
    # "amount",
    "round_time", "related_tx","inner_tx_level"
    ]
  ]

def convert_datetime(timestamp: int):
  dt_object = dt.fromtimestamp(timestamp)
  converted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
  return converted_time

# create an entry in either appl_usage or asset_usage for each transaction of that type
def generate_postgre_data(transaction: dict, level: int=0, parent_id: int=None):
  related_tx = transaction['id'] if parent_id==None else parent_id
  match transaction['tx-type']:
    case 'appl':
      appl_usage.append([
        transaction['application-transaction']['application-id'],
        convert_datetime(transaction['round-time']),
        related_tx,
        level
      ])
    case 'axfer':
      asset_usage.append([
        transaction['asset-transfer-transaction']['asset-id'],
        # transaction['asset-transfer-transaction']['amount'],
        convert_datetime(transaction['round-time']),
        related_tx,
        level
      ])
  if transaction['inner-txns'] != "N/A":
    for tx in transaction['inner-txns']:
      generate_postgre_data(transaction=tx, level=level+1, parent_id=related_tx)

def save_csv_data(
    data: list[list[str]],
    filename: str,
    directory: str ='data/postgres/'
  ):
  file_path = directory + filename
  with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)


################## Setup & Load data to PostgreSQL database ####################
import configparser
import os
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

def populate_new_table(data_file: str):
  table_name = os.path.splitext(os.path.basename(data_file))[0]
  with open(data_file,"r", newline="") as f:
    next(f) # Skip the header row
    cursor.copy_from(file=f, table=table_name,sep=',')


################################################################################
def get_meta_data(dataset: str = "1 day data"):
  with open('data/meta_data.json','r') as f:
    meta_data = json.load(f)[dataset]
  return meta_data

# def run_db_scripts(blocknr_start: int, blocknr_end: int):

if __name__ == '__main__':

  # Data collection and pre-processing (1)
  meta_data = get_meta_data(dataset="1 month data")
  start_block = meta_data["start block"]
  end_block = meta_data["end block"]

  start_block = 29709143
  crawl_and_ingestion(start=start_block, end=end_block, db_info={})

  exit()
  crawl_data(start=start_block, end=end_block)

  # Set up MongoDB database
  mongo_client = MongoClient("localhost", 27017)
  mock_db = mongo_client['defi_mock_db']
  tx_collection = mock_db['transactions']
  mongo_ingestion(collection=tx_collection)

  # extract transactions as list
  mongo_txns = list(tx_collection.find({}))
  mongo_client.close()

  # Prepare data for Postgres
  for tx in mongo_txns:
    generate_postgre_data(transaction=tx)
  save_csv_data(data=appl_usage, filename="appl_usage.csv")
  save_csv_data(data=asset_usage, filename="asset_usage.csv")

  # Setup Postgres
  pg_params = pg_parameters_extract(PG_CONFIG)

  conn = psycopg2.connect(
      dbname=pg_params["dbname"],
      user=pg_params["user"],
      password=pg_params["password"],
      host=pg_params["host"],
      port=pg_params["port"]
  )
  cursor = conn.cursor()

  # Load data to Postgres
  populate_new_table(data_file='data/postgres/appl_usage.csv')
  populate_new_table(data_file='data/postgres/asset_usage.csv')
  populate_new_table(data_file='data/postgres/dexs.csv')

  conn.commit()
  conn.close()