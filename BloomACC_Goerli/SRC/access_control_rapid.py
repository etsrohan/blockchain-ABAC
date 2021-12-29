# Import Modules/Functions
from web3 import Web3, middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json
import threading

subject_address_list = [
    "0x6a09436F3Cb7C3e871071033ABA967327499b9d4",
    "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a",
    "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B",
    "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23",
    "0xa72e420605FD940b860c493263ce891d434782CB"
]

subject_dict = {
    "0x6a09436F3Cb7C3e871071033ABA967327499b9d4": "890d4a07e4f4aa790111fe8b2a5d07c84de8a708d51c48487416b892b905c010",
    "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a": "a2a0d0097c87754d45cff13ecb81f697b30106db553250eea411da48ca5bef4a",
    "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B": "ef741d30314c0cfa147f2c0f409349c587a5a27b4003b8e5cdf0490e6eaa588d",
    "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23": "64778725d0104b96b58dad5d21bce443b806bf322b4d58d82afc60b279532a0c",
    "0xa72e420605FD940b860c493263ce891d434782CB": "a18a2c18ed46edb5b6c4fe2a52a69373c7929b34489ac9b193cc313ff2a01c7d"
}

object_address_list = [
    "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D",
    "0xe1ac1b434331F1c57b909947eC20393819Ad462f",
    "0xD9c258d8aA168add0E5183C9725c1C7C0712868A",
    "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90",
    "0x877f503365C0b55F4259208D4327daF6BDC66d01"
]

# object_dict = {
#     "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D": "91b403bd0ced9eff20eb3c8bf388bdc5641fa33978770ac8487ca7406950cb0d",
#     "0xe1ac1b434331F1c57b909947eC20393819Ad462f": "d1b539ffd7dd1624370b09025ec2f6d649e9c8e7c55077370d696e181effe83a",
#     "0xD9c258d8aA168add0E5183C9725c1C7C0712868A": "b4d3426cd39722b35050289379616ff6d0dd4e8c6256881a4601daf826d2bab8",
#     "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90": "b637439846fab4659ee39e98ab8655f5e2f5ca719c25fb9004426fe9d0a361dd",
#     "0x877f503365C0b55F4259208D4327daF6BDC66d01": "876545b242014e371ab56e55f5553d5efda45b73df4280c7bc13754224fead9a"
# }

# Global Variables
ADDR = "0xD5956cfB4Bb948ADcE1033580b85257C624c29d7"
PRIVATE_KEY = "8feaed78e867d6aebd5bab7c5f835b25a0f17b7f191316d16650e63d9bd16ecf"
# Connect to Goerli
INFURA_URL = "https://goerli.infura.io/v3/60febbc1f74c4e229c6f6f694ea571ac"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer = 0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GOERLI TEST NETWORK\n')

# set default account to manufacturer
w3.eth.default_account = ADDR

# Open and get Access ABI/Address
with open('Info/AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()
# Open and get SubjectContract ABI/Address
with open('Info/SubjectAttribute.contract', 'r') as file_obj:
    subject_info = file_obj.readlines()

# print(object_info)
# Gives a list of adderss and abi
# Get address/abi for object contract
access_address = access_info[0][:-1]
access_abi = json.loads(access_info[1])

# print(subject_info)
# Gives a list of adderss and abi
# Get address/abi for subject contract
subject_address = subject_info[0][:-1]
subject_abi = json.loads(subject_info[1])

# Connecting to object contract
access_contract = w3.eth.contract(
    address = access_address,
    abi = access_abi
)

# Connecting to subject contract
subject_contract = w3.eth.contract(
    address = subject_address,
    abi = subject_abi
)

# Setting Strategy, Nonce, and Gas Price
strategy = construct_time_based_gas_price_strategy(15)
w3.eth.set_gas_price_strategy(strategy)


gas_price = w3.eth.generate_gas_price()
print("Gas Price: ", gas_price)
# --------------------------MAIN PROGRAM----------------------------
# Access control ABI:
# sub_id, obj_id, action all are ints

# Subject Attributes:
#   Manufacturer, current_location, vehicle_type, charging_efficiency
#   discharging_efficiency, energy_capacity, ToMFR

def send_request(sub, obj, action):
    nonce = w3.eth.get_transaction_count(sub)
    tr = {
        'from': sub,
        'gasPrice': Web3.toHex(gas_price),
        'nonce': Web3.toHex(nonce)
    }
    
    nonce -= 1

    while True:
        nonce += 1
        tr["nonce"] = Web3.toHex(nonce)
        
        # Build transaction
        txn = access_contract.functions.access_control(obj, action).buildTransaction(tr)
        # Sign the transaction
        signed = w3.eth.account.sign_transaction(txn, subject_dict[sub])
        # Send raw transaction
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        # wait for the transaction to be mined and get the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f'\nSent Access Request for sub_addr: {sub[-4:]} obj_addr: {obj[-4:]} and action: {action}\n')
    
threads = []
for index in range(5):
    thread = threading.Thread(
        target = send_request,
        args = (subject_address_list[index], object_address_list[index], 0)
    )
    threads.append(thread)

for thread in threads:
    thread.start()