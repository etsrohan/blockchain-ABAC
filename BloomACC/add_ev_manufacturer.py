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

with open('SubjectAttribute.contract', 'r') as file_obj:
    subject_info = file_obj.readlines()

# print(subject_info)
# Gives a list of adderss and abi
# Get address/abi for subject contract
subject_address = subject_info[0][:-1]
subject_abi = json.loads(subject_info[1])

# Connecting to subject contract
subject_contract = w3.eth.contract(
    address = subject_address,
    abi = subject_abi
)

# --------------------------MAIN PROGRAM----------------------------

# Send a transaction to add the 2 manufacturers index 11, 12
for address in w3.eth.accounts[11:13]:
    print(f'[Admin] Adding EV Manufacturer 0x...{address[-4:]}')
    tx_hash = subject_contract.functions.add_ev_man(address).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print('[SUCCESS] EV Manufacturers added!')