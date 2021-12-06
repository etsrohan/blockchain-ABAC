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

# Open and get Token ABI/Address
with open('EVToken.contract', 'r') as file_obj:
    token_info = file_obj.readlines()
# Get address/abi for token contract
token_address = token_info[0][:-1]
token_abi = json.loads(token_info[1])

# Open and get Access ABI/Address
with open('AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()
# Get address/abi for access contract
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

# Connecting to token contract
token_contract = w3.eth.contract(
    address = token_address,
    abi = token_abi
)

# Connecting to access contract
access_contract = w3.eth.contract(
    address = access_address,
    abi = access_abi
)

# --------------------------MAIN PROGRAM----------------------------
print("[WAITING] Listening for new events...")

# HANDLE FUNCTIONS
def handle_access(sub_id, obj_id, action, access, message):
    """
    Function to handle the event of a access request.
    If access is granted (access = 1) then prints success message
    If access is denied (access = 2) then prints failure message
    """
    if access == 1:
        print(f'\n[SUCCESS] Access Granted!\nsub_id: {sub_id}\nobj_id:{obj_id}\naction:{action}')
    elif access == 2:
        print(f'\n[FAILURE] Access Denied!\nsub_id: {sub_id}\nobj_id:{obj_id}\naction:{action}\nmessage: {message}')
    else:
        print('\n[ERROR] INVALID ACCESS VARIABLE!')
        

def handle_new_pol(pol_id):
    """
    Function to handle the event of a new policy
    being added and get the assigned pol_id
    """
    print(f'\nNew Policy Added! pol_id: {pol_id}')

def handle_new_sub(sub_id, manufacturer):
    """
    Function to handle the event of a new subject
    being added and get the assigned sub_id
    """
    print(f'\nNew Subject Added! {manufacturer} with sub_id: {sub_id}')

def handle_new_obj(obj_id, location):
    """
    Function to handle the event of a new object
    being added and get the assigned obj_id
    """
    print(f'\nNew Object Added! {location} with obj_id: {obj_id}')

def handle_transfer(owner, receiver, num_tokens, expiration_time):
    """
    Function to handle the event of a new transfer of EVToken
    from an owner to a receiver, num_tokens is the number of tokens transferred
    """
    print(f'''\n[SUCCESS] EVToken Transferred-\n
              \r\tSubject: 0x...{receiver[-4:]}\n
              \r\tAdmin: 0x...{owner[-4:]}\n
              \r\tAmount: {num_tokens}\n
              \r\tExpiration Time: {expiration_time}\n''')
    
def handle_auth_succ(sub_id):
    """
    Function to handle the event of authentication success of a subject
    """
    print(f'\nAuthentication Success: {sub_id}\n')
    
def handle_auth_fail(sub_id):
    """
    Function to handle the event of authentication failure of a subject
    """
    print(f'\nAuthentication Failure: {sub_id}\n')
    
def handle_sub_change(sub_id):
    """
    Function to handle the event of subject attributes being changed
    """
    print(f'''\nSubject Attributes changed: 
              \r\tSubject ID: {sub_id}\n''')
    
# ASYNC FUNCTIONS
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
                    2,
                    access_denied['args']['message']
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
                    1,
                    ''
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
                    new_sub_added['args']['manufacturer']
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
                    new_obj_added['args']['location']
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

async def auth_success_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every authentication
    success
    """
    
    while True:
        for success in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_auth_succ,
                args = (
                    success['args']['sub_id'],
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

async def auth_fail_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every authentication
    failure
    """
    
    while True:
        for failure in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_auth_fail,
                args = (
                    failure['args']['sub_id'],
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

async def transfer_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every transfer of tokens
    taking place
    """
    
    while True:
        for new_transfer in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_transfer,
                args = (
                    new_transfer['args']['admin'],
                    new_transfer['args']['receiver'],
                    new_transfer['args']['num_tokens'],
                    new_transfer['args']['expiration_time']
                ))
            thread.start()
        await asyncio.sleep(poll_interval)
        
async def sub_change_loop(event_filter, poll_interval):
    """
    Asynchronous function to create new threads for every change in subject
    attributes
    """
    
    while True:
        for change in event_filter.get_new_entries():
            thread = threading.Thread(
                target = handle_sub_change,
                args = (
                    change['args']['sub_id'],
                ))
            thread.start()
        await asyncio.sleep(poll_interval)

# Main Function 
def main():
    subject_filter = subject_contract.events.NewSubjectAdded().createFilter(fromBlock = 'latest')
    sub_change_filter = subject_contract.events.SubjectChanged().createFilter(fromBlock = 'latest')
    object_filter = object_contract.events.NewObjectAdded().createFilter(fromBlock = 'latest')
    policy_filter = policy_contract.events.PolicyAdded().createFilter(fromBlock = 'latest')
    access_success = access_contract.events.AccessGranted().createFilter(fromBlock = 'latest')
    access_failure = access_contract.events.AccessDenied().createFilter(fromBlock = 'latest')
    authentication_success = access_contract.events.AuthenticationSuccess().createFilter(fromBlock = 'latest')
    authentication_failure = access_contract.events.AuthenticationFailure().createFilter(fromBlock = 'latest')
    transfer_filter = token_contract.events.AdminTransfer().createFilter(fromBlock = 'latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                sub_loop(subject_filter, 2),
                obj_loop(object_filter, 2),
                pol_loop(policy_filter, 2),
                succ_loop(access_success, 2),
                fail_loop(access_failure, 2),
                transfer_loop(transfer_filter, 2),
                auth_success_loop(authentication_success, 2),
                auth_fail_loop(authentication_failure, 2),
                sub_change_loop(sub_change_filter, 2)
                )
            )
    finally:
        loop.close()

if __name__ == '__main__':
    main()