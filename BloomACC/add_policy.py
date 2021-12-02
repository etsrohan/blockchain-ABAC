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

with open('PolicyManagement.contract', 'r') as file_obj:
    policy_info = file_obj.readlines()

# print(policy_info)
# Gives a list of adderss and abi
# Get address/abi for policy contract
policy_address = policy_info[0][:-1]
policy_abi = json.loads(policy_info[1])

# Connecting to policy contract
policy_contract = w3.eth.contract(
    address = policy_address,
    abi = policy_abi
)
# --------------------------MAIN PROGRAM----------------------------
# Policy Content:
# Subject = (Manufacturer, current_location, vehicle_type, charging_efficiency, discharging_efficiency, energy_capacity, ToMFR)
# Object = (Avg. Waiting Time, Location, Avg. charging time, number of charging outlets, Charging Power, Utilization Rate)
# Action = (read, write, execute)
# Context = (min_interval, start_time, end_time)
# policy add ABI expects 4 inputs: subject list, object list, action list, context list

# Send policy function to send policy_add transaction
def send_policy(policy):
    """
    Function which is used as a target for threading to send
    transactions to add new policies to PolicyManagementContract
    """
    # Split policy into subject, object, action, con_mode and con_time
    policy = policy.split(':')
    if len(policy) != 4:
        print('[ERROR] INVALID POLICY. MAKE SURE POLICY HAS 4 PARTS.')
        return
    
    for i in range(4):
        policy[i] = policy[i].split(';')

    # Loop through every context and turn it into boolean
    for i in range(3):
        if policy[2][i].lower() == 'true':
            policy[2][i] = True
        else:
            policy[2][i] = False
    
    # Convert context into list of 3 ints
    for i in range(3):
        policy[3][i] = int(policy[3][i])
    
    # Send policy_add transaction
    tx_hash = policy_contract.functions.policy_add(*policy).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"""[SUCCESS] Added policy:\n
          \r\t{policy[0]}\n
          \r\t{policy[1]}\n
          \r\t{policy[2]}\n
          \r\t{policy[3]}\n""")
    
# Get policies from policies.txt
with open('policies.txt', 'r') as file_obj:
    policy_info = file_obj.readlines()

# For every policy in policy_info send policy_add transaction 
threads = []
for policy in policy_info:
    # If policy line ends with \n then remove it
    if policy[-1] == '\n':
        policy = policy[:-1]
    # Create a new thread for every policy
    thread = threading.Thread(
        target = send_policy,
        args = (policy,)
    )
    # Add thread to threads list
    threads.append(thread)
# Start every thread of send_policy
for thread in threads:
    thread.start()
# Wait for threads to finish before calling get_policy
for thread in threads:
    thread.join()
# Call get_policy abi to confirm that every policy was added successfully.
for i in range(len(policy_info)):
    print('Policy:\n\t', policy_contract.functions.get_policy(i).call())
print('\n[ADD POLICY][SUCCESS] Transactions Successful\n')