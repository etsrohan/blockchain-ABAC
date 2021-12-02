# Import Modules/Functions
from web3 import Web3
import json

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

with open('EVToken.contract', 'r') as file_obj:
    token_info = file_obj.readlines()

# print(token_info)
# Gives a list of address and abi
# Get address/abi for object contract
token_address = token_info[0][:-1]
token_abi = json.loads(token_info[1])

# Connecting to token contract
token_contract = w3.eth.contract(
    address = token_address,
    abi = token_abi
)

# Get the AccessControl Contract address
with open('AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()

access_address = access_info[0][:-1]

# --------------------------MAIN PROGRAM----------------------------

# Send a transaction to set AccessControl Contract address in EVToken Contract
tx_hash = token_contract.functions.set_access_address(access_address).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f'[Success] Set AccessControl Contract address 0x...{access_address[-4:]} for EVToken')
