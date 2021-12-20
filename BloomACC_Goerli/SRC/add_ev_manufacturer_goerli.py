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

with open('Info/SubjectAttribute.contract', 'r') as file_obj:
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
ev_man_addresses = [
    "0x59e8e60540c5204402Ee39490381c206B77fc7eE",
    "0xD5956cfB4Bb948ADcE1033580b85257C624c29d7"
]
nonce -= 1
# Send a transaction to add the 2 manufacturers index 11, 12 in ACCOUNTS DICT in test connection script
for address in ev_man_addresses:
    print(f'[Admin] Adding EV Manufacturer 0x...{address[-4:]}')
    
    nonce += 1
    tr['nonce'] = Web3.toHex(nonce)
    # Build Constructor Transaction
    txn = subject_contract.functions.add_ev_man(address).buildTransaction(tr)
    # Sign the transaction
    signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    # Send raw transaction
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
print('[SUCCESS] EV Manufacturers added!')
print(f'0x...{ev_man_addresses[0][-4:]}')
print(f'0x...{ev_man_addresses[1][-4:]}')