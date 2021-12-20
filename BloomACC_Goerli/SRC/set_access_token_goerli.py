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

with open('Info/EVToken.contract', 'r') as file_obj:
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
with open('Info/AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()

access_address = access_info[0][:-1]

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

# Send a transaction to set AccessControl Contract address in EVToken Contract
print(f'[EXECUTING] Setting ACC Address to admin status in EVToken Contract...')

# Build Constructor Transaction
txn = token_contract.functions.set_access_address(access_address).buildTransaction(tr)
# Sign the transaction
signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
# Send raw transaction
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f'[Success] Set AccessControl Contract address 0x...{access_address[-4:]} for EVToken')
