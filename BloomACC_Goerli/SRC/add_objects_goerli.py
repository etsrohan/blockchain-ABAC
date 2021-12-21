# Import Modules/Functions
from web3 import Web3, middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json

object_address_list = [
    "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D",
    "0xe1ac1b434331F1c57b909947eC20393819Ad462f",
    "0xD9c258d8aA168add0E5183C9725c1C7C0712868A",
    "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90",
    "0x877f503365C0b55F4259208D4327daF6BDC66d01"
]

# Global Variables
ADDR = "0x0cE5C86d596cB1446f561503c33721Ca43236603"
PRIVATE_KEY = "09892cc8797addb00fd5b0c69802e0ee4ae3f776a63b63a82a86c7ebf083c3e9"
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
# Object Attributes:
#   Plug Type, Location, Pricing Model, Number of Charging Outlets
#   Charging Power, Fast Charging

# Send object function to send object_add transaction
def send_object(address, object, tr):
    """
    Function which is used as a target for threading to send
    transactions to add new objects to ObjectAttributeContract
    """
    txn = object_contract.functions.object_add(address, object.split(';')).buildTransaction(tr)
    # Sign the transaction
    signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    # Send raw transaction
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"[SUCCESS] Added object {object.split(';')[1]}")

# Get objects data from objects.txt
with open('Attributes/objects.txt', 'r') as file_obj:
    obj_info = file_obj.readlines()

nonce -= 1
# For every object in obj_info send object_add transaction 
for index, obj in enumerate(obj_info):
    # Remove \n at the end of each string if it exists
    if obj[-1] == '\n':
        obj = obj[:-1]
    # Update nonce
    nonce += 1
    tr['nonce'] = Web3.toHex(nonce)
    # Send add_object transaction
    print('\nAdding new Object')
    send_object(object_address_list[index], obj, tr)

# Call objects abi to confirm that every object was added successfully.
for address in object_address_list:
    print('Object:\n\t', object_contract.functions.objects(address).call())
print('\n[ADD OBJECTS][SUCCESS] Transactions Successful\n')