# Import Modules/Functions
from web3 import Web3
import threading
import json

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

with open('Info/ObjectAttribute.contract', 'r') as file_obj:
    object_info = file_obj.readlines()

# print(object_info)
# Gives a list of adderss and abi
# Get address/abi for object contract
object_address = object_info[0][:-1]
object_abi = json.loads(object_info[1])

# Connecting to object contract
object_contract = w3.eth.contract(
    address = object_address,
    abi = object_abi
)

# --------------------------MAIN PROGRAM----------------------------

address = w3.eth.accounts[13]
# Send a transaction to add the cs leader at index 13
print(f'[Admin] Adding CS Leader 0x...{address[-4:]}')
tx_hash = object_contract.functions.add_cs_leader(address).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print('[SUCCESS] CS Leader added!')