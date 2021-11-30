# Import Modules/Functions
from re import sub
from web3 import Web3
import json

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[1]

# Open and get Access ABI/Address
with open('AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()

# print(object_info)
# Gives a list of adderss and abi
# Get address/abi for object contract
access_address = access_info[0][:-1]
access_abi = json.loads(access_info[1])

# Connecting to object contract
access_contract = w3.eth.contract(
    address = access_address,
    abi = access_abi
)
# --------------------------MAIN PROGRAM----------------------------
# Access control ABI:
# sub_id, obj_id, action all are ints

sub_id = int(input('Please enter your sub_id: '))
obj_id = int(input('Please enter the obj_id: '))
action = int(input('Please enter the action you want to perform: '))
tx_hash = access_contract.functions.access_control(sub_id, obj_id, action).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Sent Access Request for sub_id: {sub_id} obj_id: {obj_id} and action: {action}')