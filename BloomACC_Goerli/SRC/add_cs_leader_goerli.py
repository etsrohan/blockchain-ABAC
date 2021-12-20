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

with open('Info/ObjectAttribute.contract', 'r') as file_obj:
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

cs_leader_address = "0x0cE5C86d596cB1446f561503c33721Ca43236603"
# Send a transaction to add the cs leader at index 13 of ACCOUNTS DICT in test connection script
print(f'[Admin] Adding CS Leader 0x...{cs_leader_address[-4:]}')

# Build Constructor Transaction
txn = object_contract.functions.add_cs_leader(cs_leader_address).buildTransaction(tr)
# Sign the transaction
signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
# Send raw transaction
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f'[SUCCESS] CS Leader added!\n0x...{cs_leader_address[-4:]}')