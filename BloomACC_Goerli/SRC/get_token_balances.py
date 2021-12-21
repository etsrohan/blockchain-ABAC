# Import Modules/Functions
from web3 import Web3, middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json

addr_list = [
    "0x6a09436F3Cb7C3e871071033ABA967327499b9d4",
    "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a",
    "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B",
    "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23",
    "0xa72e420605FD940b860c493263ce891d434782CB",
    "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D",
    "0xe1ac1b434331F1c57b909947eC20393819Ad462f",
    "0xD9c258d8aA168add0E5183C9725c1C7C0712868A",
    "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90",
    "0x877f503365C0b55F4259208D4327daF6BDC66d01"
]

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

# --------------------------MAIN PROGRAM----------------------------

# For every address on ganache network call get_balance abi from token contract
for address in addr_list:
    print(f'Balance[0x...{address[-4:]}]: {token_contract.functions.get_balance(address).call()}')