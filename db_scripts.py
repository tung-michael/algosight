# For setting up and populating data base
import json
import requests
from pymongo import MongoClient


API_URL = 'https://mainnet-idx.algonode.cloud'
BLOCK_ENDPOINT = '/v2/blocks/'
TX_FIELDS = ["id", "tx-type", "sender", "fee", "confirmed-round", "group", "inner-txns"]


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
tx_col = mock_db['transactions']

# with open("data/mongo/clean_data.json") as file:
#   txns = json.load(file)

tx_col.insert_many(txns)

mongo_client.close()
exit()



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