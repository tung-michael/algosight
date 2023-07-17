import json
import requests
from dataclasses import fields, asdict
from DataModels import Account, Transaction, PaymentTx, ApplicationCallTx, AssetTransferTx
import View as view

# def cls_field_name(class_name):
#   try:
#     obj_fields = [f.name for f in fields(class_name)]
#     return obj_fields
#   except TypeError:
#       pass

# print(fields(PaymentTx))
# for f in fields(PaymentTx):
#   if f.name == "tx_id":
#     print(f)
#   if f.name == "group_id":
#     print(f)

with open("data/raw_part.json") as file:
  json_data = json.load(file)

def scrape_tx_data(tx_list: list, parent_id: str=None):
  depth = 0
  transactions = []
  for tx in tx_list:
    mapped_data = {}
    for field in Transaction.__annotations__.keys():
      try:
        if field != 'inner_txns':
          mapped_data[field] = tx[Transaction.field_mapping().get(field,field)]
        else:
            if 'inner-txns' in tx:
              transactions.extend(scrape_tx_data(tx['inner-txns'], parent_id=tx['id']))
              depth+=1
              print(depth)
              # mapped_data['inner_tx'] = True
              mapped_data['inner_txns'] = len(tx['inner-txns'])
            if 'tx-type' in tx:
              print("Obviously") # [DELETE THIS]
      except KeyError as e:
        if e.args[0] in ['group']:
          pass
        elif e.args[0] == 'id':
          mapped_data['tx_id'] = parent_id
        else:
          raise
    if tx['tx-type'] == 'pay':
      for field in PaymentTx.__annotations__.keys():
          mapped_data[field] = tx["payment-transaction"][field]
      tx_obj = PaymentTx(**mapped_data)
      transactions.append(asdict(tx_obj))

    elif tx['tx-type'] == 'axfer':
      for field in AssetTransferTx.__annotations__.keys():
          mapped_data[field] = tx["asset-transfer-transaction"][AssetTransferTx.field_mapping().get(field,field)]
      tx_obj = AssetTransferTx(**mapped_data)
      transactions.append(asdict(tx_obj))

    elif tx['tx-type'] == 'appl':
      for field in ApplicationCallTx.__annotations__.keys():
          mapped_data[field] = tx["application-transaction"][ApplicationCallTx.field_mapping().get(field,field)]
      tx_obj = ApplicationCallTx(**mapped_data)
      transactions.append(asdict(tx_obj))
  return transactions


############################################
txns = []
for block in json_data:
  txns.extend(scrape_tx_data(tx_list=block['transactions']))


with open('data/clean_data.json', 'w', encoding='utf-8') as f:
    json.dump(txns, f, ensure_ascii=False, indent=4)
exit()
axfer_txs = []
pay_txs = []
appl_txs = []
keyreg_txs = []
acfg_txs = []
afrz_txs = []
other_txs = []

  # for tx in block['transactions']:
  #   mapped_data = {}
  #   # for kw in cls_field_name(Transaction):
  #   for kw in Transaction.__annotations__.keys():
  #     try:
  #       mapped_data[kw] = tx[Transaction.field_mapping().get(kw,kw)]
  #     except KeyError as e:
  #       if e.args[0] in ['group', 'inner_txns']:
  #         pass
  #       else:
  #         raise
  #   if tx['tx-type'] == 'pay':
  #     for kw in PaymentTx.__annotations__.keys():
  #         mapped_data[kw] = tx["payment-transaction"][kw]
  #     tx_obj = PaymentTx(**mapped_data)
  #     transactions.append(asdict(tx_obj))

  #   if tx['tx-type'] == 'axfer':
  #     for kw in AssetTransferTx.__annotations__.keys():
  #         mapped_data[kw] = tx["asset-transfer-transaction"][AssetTransferTx.field_mapping().get(kw,kw)]
  #     tx_obj = AssetTransferTx(**mapped_data)
  #     transactions.append(asdict(tx_obj))

  #   if tx['tx-type'] == 'appl':
  #     for kw in ApplicationCallTx.__annotations__.keys():
  #         mapped_data[kw] = tx["application-transaction"][ApplicationCallTx.field_mapping().get(kw,kw)]
  #     tx_obj = ApplicationCallTx(**mapped_data)
  #     transactions.append(asdict(tx_obj))
"""
total number of txns is 3549
axfer_txs: 1133
pay_txs: 686
appl_txs: 1544
keyreg_txs: 0
acfg_txs: 185
afrz_txs: 0
other_txs: ['stpf']
"""


#####################################################################

# call_1 = '/v2/accounts/SVZS7Q7QMVHZONDHZJHR4564VTMEX3OQ5DSYBWKR5FJFTPZLVG3EZIWC34/transactions?limit=5' # 5 HUMBLESWAP transactions
# call_2 = '/v2/accounts/SVZS7Q7QMVHZONDHZJHR4564VTMEX3OQ5DSYBWKR5FJFTPZLVG3EZIWC34/transactions?before-time=2023-06-29T09%3A30%3A00%2B02%3A00&after-time=2023-06-29T09%3A00%3A00%2B02%3A00'

# call_block ='/v2/blocks/30441636'

# r = requests.get(API_URL + call_block)

# print(r.status_code)
# response = r.json()

# print(len(response['transactions']))

# for t in response['transactions']:
#   if t['tx-type'] == 'axfer':
#     print(t)

# print(['transactions'][2])

# 1. fetch all transactions of an account that were executed
# between 2023-06-29T09:00:00+02:00 and 2023-06-29T09:30:00+02:00
# 2. count the number of 'transfer transaction' per each asset



class Controller:
  def __init__(self) -> None:
    pass

