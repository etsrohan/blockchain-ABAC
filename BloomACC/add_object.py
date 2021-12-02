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

with open('ObjectAttribute.contract', 'r') as file_obj:
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
# Object Attributes:
#   Avg. Waiting Time, Location, Avg. charging time, number of charging outlets
#   Charging Power, Utilization Rate

# Send object function to send object_add transaction
def send_object(object):
    """
    Function which is used as a target for threading to send
    transactions to add new objects to ObjectAttributeContract
    """
    tx_hash = object_contract.functions.object_add(object.split(';')).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[SUCCESS] Added object {object.split(';')[1]}")

# Get objects data from objects.txt
with open('objects.txt', 'r') as file_obj:
    obj_info = file_obj.readlines()

# For every object in obj_info send object_add transaction 
threads = []
for obj in obj_info:
    # Remove \n at the end of each string if it exists
    if obj[-1] == '\n':
        obj = obj[:-1]
    # Create a new thread for every object
    thread = threading.Thread(
        target = send_object,
        args = (obj,)
    )
    # Add thread to threads list
    threads.append(thread)
# Start the threads in threads list
for thread in threads:
    thread.start()
# Wait for threads to finish before calling objects
for thread in threads:
    thread.join()
# Call objects abi to confirm that every object was added successfully.
for i in range(len(obj_info)):
    print('Object:\n\t', object_contract.functions.objects(i).call())
print('\n[ADD OBJECTS][SUCCESS] Transactions Successful\n')