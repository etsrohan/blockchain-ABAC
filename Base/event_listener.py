# Import Modules/Functions
from web3 import Web3
import threading
import json
import asyncio

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

# Open and get Object ABI/Address
with open('ObjectAttribute.contract', 'r') as file_obj:
    object_info = file_obj.readlines()
# Get address/abi for object contract
object_address = object_info[0][:-1]
object_abi = json.loads(object_info[1])

# Open and get Subject ABI/Address
with open('SubjectAttribute.contract', 'r') as file_obj:
    subject_info = file_obj.readlines()
# Get address/abi for subject contract
subject_address = subject_info[0][:-1]
subject_abi = json.loads(subject_info[1])

# Open and get Policy ABI/Address
with open('PolicyManagement.contract', 'r') as file_obj:
    policy_info = file_obj.readlines()
# Get address/abi for policy contract
policy_address = policy_info[0][:-1]
policy_abi = json.loads(policy_info[1])

# Open and get Access ABI/Address
with open('AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()
# Get address/abi for object contract
access_address = access_info[0][:-1]
access_abi = json.loads(access_info[1])

# Connect to object contract
object_contract = w3.eth.contract(
    address = object_address,
    abi = object_abi
)

# Connect to subject contract
subject_contract = w3.eth.contract(
    address = subject_address,
    abi = subject_abi
)

# Connect to policy contract
policy_contract = w3.eth.contract(
    address = policy_address,
    abi = policy_abi
)

# Connecting to access contract
access_contract = w3.eth.contract(
    address = access_address,
    abi = access_abi
)

# --------------------------MAIN PROGRAM----------------------------
print("[WAITING] Listening for new events...")
def handle_access(sub_id, obj_id, action, access):
    """
    Function to handle the event of a access request.
    If access is granted (access = 1) then prints success message
    If access is denied (access = 2) then prints failure message
    """
    if access == 1:
        print(f'\n[SUCCESS] Access Granted!\nsub_id: {sub_id}\nobj_id:{obj_id}\naction:{action}')
    elif access == 2:
        print(f'\n[FAILURE] Access Denied!\nsub_id: {sub_id}\nobj_id:{obj_id}\naction:{action}')
    else:
        print('\n[ERROR] INVALID ACCESS VARIABLE!')
        

def handle_new_pol(pol_id):
    """
    Function to handle the event of a new policy
    being added and get the assigned pol_id
    """
    print(f'\nNew Policy Added! pol_id: {pol_id}')

def handle_new_sub(sub_id, name):
    """
    Function to handle the event of a new subject
    being added and get the assigned sub_id
    """
    print(f'\nNew Subject Added! {name} with sub_id: {sub_id}')

def handle_new_obj(obj_id, name):
    """
    Function to handle the event of a new object
    being added and get the assigned obj_id
    """
    print(f'\nNew Object Added! {name} with obj_id: {obj_id}')
    
async def fail_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every unsuccessful
    access granted(access denied) by AccessControlContract
    """
    
    while True:
        for access_denied in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_access,
                args = (
                    access_denied['args']['sub_id'],
                    access_denied['args']['obj_id'],
                    access_denied['args']['action'],
                    2
                ))
            thread.start()
        await asyncio.sleep(poll_interval)
    
async def succ_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every successful
    access granted by AccessControlContract
    """
    
    while True:
        for access_granted in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_access,
                args = (
                    access_granted['args']['sub_id'],
                    access_granted['args']['obj_id'],
                    access_granted['args']['action'],
                    1
                ))
            thread.start()
        await asyncio.sleep(poll_interval)
    
async def pol_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every policy added
    to PolicyManagementContract
    """
    
    while True:
        for new_pol_added in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_new_pol,
                args = (
                    new_pol_added['args']['pol_id'],
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

async def sub_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every subject added
    to SubjectAttributeContract
    """
    
    while True:
        for new_sub_added in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_new_sub,
                args = (
                    new_sub_added['args']['sub_id'],
                    new_sub_added['args']['name']
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

async def obj_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every object added
    to ObjectAttributeContract
    """
    
    while True:
        for new_obj_added in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_new_obj,
                args = (
                    new_obj_added['args']['obj_id'],
                    new_obj_added['args']['name']
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

# Main Function 
def main():
    subject_filter = subject_contract.events.NewSubjectAdded().createFilter(fromBlock = 'latest')
    object_filter = object_contract.events.NewObjectAdded().createFilter(fromBlock = 'latest')
    policy_filter = policy_contract.events.PolicyAdded().createFilter(fromBlock = 'latest')
    access_success = access_contract.events.AccessGranted().createFilter(fromBlock = 'latest')
    access_failure = access_contract.events.AccessDenied().createFilter(fromBlock = 'latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                sub_loop(subject_filter, 2),
                obj_loop(object_filter, 2),
                pol_loop(policy_filter, 2),
                succ_loop(access_success, 2),
                fail_loop(access_failure, 2)
                )
            )
    finally:
        loop.close()

if __name__ == '__main__':
    main()