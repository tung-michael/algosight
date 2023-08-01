# For setting up and populating data base
import json
import requests
from pymongo import MongoClient


API_URL = 'https://mainnet-idx.algonode.cloud'
BLOCK_ENDPOINT = '/v2/blocks/'
TX_FIELDS = ["id", "tx-type", "sender", "fee",
             "confirmed-round", "group", "inner-txns", "round-time"]

#[TODO]: code refactoring to use this script from command line?

def fetch_blocks(start: int, end: int) -> list:
  data = []
  for block_nr in range(start, end+1):
    block = requests.get(API_URL+BLOCK_ENDPOINT+f"{block_nr}").json()
    data.append(block)
  return data


def field_filter(transaction: dict) -> dict:
  filtered_tx = {}
  match transaction["tx-type"]:
    case "appl":
      filtered_tx["application-transaction"] = transaction["application-transaction"]
    case "axfer":
      filtered_tx["asset-transfer-transaction"] = transaction["asset-transfer-transaction"]
    case "pay":
      filtered_tx["payment-transaction"] = transaction["payment-transaction"]
  for field in TX_FIELDS:
    if field in transaction.keys():
      if field == "inner-txns":
        filtered_tx["inner-txns"] = []
        for tx in transaction["inner-txns"]:
          filtered_tx["inner-txns"].append( field_filter(transaction=tx))
      else:
        filtered_tx[field] = transaction[field]
    else:
      filtered_tx[field] = "N/A"
  return filtered_tx


################## Fetch, clean, store data as JSON files ######################

blocks = fetch_blocks(30441537,30441636)
with open('data/mongo/raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(blocks, f, ensure_ascii=False, indent=4)

txns = [] # clean transactions
with open('data/mongo/clean_data.json', 'w', encoding='utf-8') as f:
  for block in blocks:
    for tx in block['transactions']:
      txns.append(field_filter(transaction=tx))
  json.dump(txns, f, ensure_ascii=False, indent=4)


######################### Set up MongoDB database ##############################

mongo_client = MongoClient("localhost", 27017)
mock_db = mongo_client['defi_mock_db']
tx_collection = mock_db['transactions']

# with open("data/mongo/clean_data.json") as file:
#   txns = json.load(file)

tx_collection.insert_many(txns)

mongo_client.close()
exit()

################# Prepare data for PostgreSQL database #########################
from datetime import datetime as dt


mongo_client = MongoClient("localhost", 27017)
mock_db = mongo_client['defi_mock_db']
tx_collection = mock_db['transactions']
mongo_txns = list(tx_collection.find({}))

mongo_client.close()

appl_usage = [["app_id", "round_time", "related_tx", "inner_tx_level"]]
asset_usage = [["asset_id", "amount", "round_time", "related_tx",
                 "inner_tx_level"]]

def convert_datetime(timestamp: int):
  dt_object = dt.fromtimestamp(timestamp)
  converted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
  return converted_time

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
        transaction['asset-transfer-transaction']['amount'],
        convert_datetime(transaction['round-time']),
        related_tx,
        level
      ])
  if transaction['inner-txns'] != "N/A":
    for tx in transaction['inner-txns']:
      generate_postgre_data(transaction=tx, level=level+1, parent_id=related_tx)

for tx in mongo_txns:
  generate_postgre_data(transaction=tx)

with open('data/postgres/appl_usage.csv', mode='w', newline='') as file:
  writer = csv.writer(file)
  writer.writerows(appl_usage)

with open('data/postgres/asset_usage.csv', mode='w', newline='') as file:
  writer = csv.writer(file)
  writer.writerows(asset_usage)

################## Setup & Load data to PostgreSQL database ####################
import configparser
import os

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


pg_params = pg_parameters_extract('data/postgres/database.ini')

conn = psycopg2.connect(
    dbname=pg_params["dbname"],
    user=pg_params["user"],
    password=pg_params["password"],
    host=pg_params["host"],
    port=pg_params["port"]
)
cursor = conn.cursor()

def populate_new_table(file_path: str):
  table_name = os.path.splitext(os.path.basename(file_path))[0]
  with open(file_path,"r", newline="") as f:
    next(f) # Skip the header row
    cursor.copy_from(file=f, table=table_name,sep=',')

populate_new_table(file_path='data/postgres/appl_usage.csv')

populate_new_table(file_path='data/postgres/asset_usage.csv')

conn.commit()
conn.close()


class DataRetriever:
  '''
    This class is responsible for retrieving data from database.
  '''
  def __init__(self) -> None:
    pass

  def get_data():
    pass


class DataAnalyzer:
  '''
    This class is responsible for calculating metrics.
  '''
  def __init__(self) -> None:
    pass


# To be developed for future features (updating data, real-time...)
class DataUpdater:
  def __init__(self) -> None:
    pass