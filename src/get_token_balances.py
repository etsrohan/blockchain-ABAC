# Import Modules/Functions
from web3 import Web3
import json

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

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
for address in w3.eth.accounts:
    print(f'Balance[0x...{address[-4:]}]: {token_contract.functions.get_balance(address).call()}')