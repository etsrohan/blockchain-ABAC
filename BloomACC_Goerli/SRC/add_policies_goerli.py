# Import Modules/Functions
from web3 import Web3, middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json

# Global Variables
ADDR = "0xbB66eF34814f0613a3B738288FE55553A69C44BA"
PRIVATE_KEY = "bee41af6acfa1c6f430646b8744e2f435f251db087971f38e5d9f2ea3a0b79c4"
# Connect to Goerli
INFURA_URL = "https://goerli.infura.io/v3/60febbc1f74c4e229c6f6f694ea571ac"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer = 0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GOERLI TEST NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = ADDR

with open('Info/PolicyManagement.contract', 'r') as file_obj:
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

# Setting Strategy, Nonce, and Gas Price
strategy = construct_time_based_gas_price_strategy(15)
w3.eth.set_gas_price_strategy(strategy)

nonce = w3.eth.get_transaction_count(ADDR)
gas_price = w3.eth.generate_gas_price()
print("Gas Price: ", gas_price)

tr = {
    'from': ADDR,
    'gasPrice': Web3.toHex(gas_price),
    'nonce': Web3.toHex(nonce)
}
# --------------------------MAIN PROGRAM----------------------------
# Policy Content:
# Subject = (Manufacturer, Current Location, Vehicle Type, Owner Name, License Plate Number, Energy Capacity, ToMFR)
# Object = (Plug Type, Location, Pricing Model, Number of Charging Outlets, Charging Power, Fast Charging)
# Action = (read, write, execute)
# Context = (min_interval, start_time, end_time)
# policy_add ABI expects 4 inputs: subject list, object list, action list, context list

# Send policy function to send policy_add transaction
def send_policy(policy, tr):
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
    
    # Build transaction
    txn = policy_contract.functions.policy_add(*policy).buildTransaction(tr)
    # Sign the transaction
    signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    # Send raw transaction
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"""[SUCCESS] Added policy:\n
          \r\t{policy[0]}\n
          \r\t{policy[1]}\n
          \r\t{policy[2]}\n
          \r\t{policy[3]}\n""")
    
# Get policies from policies.txt
with open('Attributes/policies.txt', 'r') as file_obj:
    policy_info = file_obj.readlines()

# For every policy in policy_info send policy_add transaction 
nonce -= 1
for policy in policy_info:
    # If policy line ends with \n then remove it
    if policy[-1] == '\n':
        policy = policy[:-1]
    # Update nonce
    nonce += 1
    tr['nonce'] = Web3.toHex(nonce)
    # send add_policy transaction
    print('\nAdding new policy')
    send_policy(policy, tr)
    
# Call get_policy abi to confirm that every policy was added successfully.
for i in range(len(policy_info)):
    print('Policy:\n\t', policy_contract.functions.get_policy(i).call())
print('\n[ADD POLICY][SUCCESS] Transactions Successful\n')