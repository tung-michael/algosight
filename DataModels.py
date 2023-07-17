from dataclasses import dataclass, field
from typing import List

FIELD_MAPPING = {
      "tx_id":"id",
      "tx_type": "tx-type",
      "confirmed_round": "confirmed-round",
      "group_id": "group",
      "inner_txns" : "inner-txns"
    }

OPTIONAL_FIELDS = []

@dataclass
class Account:
  address: str
  balances: list # TODO: this balance should be a list of tuples (asset_ID, amount)



@dataclass
class Transaction:
  tx_id: str
  tx_type: str
  sender: str
  fee: int
  # genesis_hash: str
  # first_valid: str
  # last_valid: str
  confirmed_round: int
  inner_txns: int = field(kw_only=True, default=0)
  # inner_txns: bool = field(kw_only=True, default=False)
  group_id: str = field(kw_only=True, default="None")
  # inner_tx: List['Transaction'] = field(kw_only=True, default=False)

  def field_mapping():
    result = FIELD_MAPPING.copy()
    return result


@dataclass
class PaymentTx(Transaction):
  # tx_type = 'pay'
  amount: int

@dataclass
class AssetTransferTx(Transaction):
  # tx_type = 'axfer'
  asset_id: int
  amount: int
  receiver: str

  def field_mapping():
    field_mapping = FIELD_MAPPING.copy()
    field_mapping.update({
      "asset_id" : "asset-id"
    })
    return field_mapping

@dataclass
class ApplicationCallTx(Transaction):
  # tx_type = 'appl'
  app_id: int

  def field_mapping():
    field_mapping = FIELD_MAPPING.copy()
    field_mapping.update({
      "app_id" : "application-id"
    })
    return field_mapping


# @dataclass
# class AssetFreezeTx(Transaction):
#   def __init__(self) -> None:
#     pass


# @dataclass
# class KeyRegistrationTx(Transaction):
#   def __init__(self) -> None:
#     pass


# @dataclass
# class AssetConfigTx(Transaction):
#   def __init__(self) -> None:
#     pass

