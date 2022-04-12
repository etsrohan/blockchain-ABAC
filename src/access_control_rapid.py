# Import Modules/Functions
import web3
from web3 import Web3
import json
import threading

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# Open and get Access ABI/Address
with open('Info/AccessControl.contract', 'r') as file_obj:
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
def send_request(subject, obj, action):
    while True:
        tx_hash = access_contract.functions.access_control(obj, action).transact({'from': subject})

threads = []
for index, subject in enumerate(w3.eth.accounts[1:6]):
    obj = w3.eth.accounts[index + 6]
    thread = threading.Thread(
        target = send_request,
        args = (subject, obj, 0)
    )
    threads.append(thread)

for thread in threads:
    thread.start()
