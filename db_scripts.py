# For setting up and populating data base
import json
import requests

API_URL = 'https://mainnet-idx.algonode.cloud'
BLOCK_ENDPOINT = '/v2/blocks/'


def fetch_blocks(start: int, end: int) -> list:
  data = []
  for block_nr in range(start, end+1):
    response = requests.get(API_URL+BLOCK_ENDPOINT+f"{block_nr}").json()
    data.append(response)
  return data

data = fetch_blocks(30441537,30441636)

with open('data/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


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