# Import Modules and Functions
from solcx import compile_files
import os
from web3 import Web3, middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json

# Global Variables

ADDR = "0xbB66eF34814f0613a3B738288FE55553A69C44BA"
PRIVATE_KEY = "bee41af6acfa1c6f430646b8744e2f435f251db087971f38e5d9f2ea3a0b79c4"


INFURA_URL = "https://goerli.infura.io/v3/60febbc1f74c4e229c6f6f694ea571ac"

# Getting current working directory (cwd)
cwd = os.getcwd()
# Compile ABAC Contracts
compiled_sol = compile_files([cwd + '/Contracts/AccessControlContract.sol'])

# Some important exploration
# print(os.getcwd())
# RESULT:
# /home/rohan/Desktop/Blockchain-ABAC/BloomACC

# print(compiled_sol.keys())
# RESULT:
# dict_keys(['/home/rohan/Desktop/Blockchain-ABAC/BloomACC/AccessControlContract.sol:AccessControl', 
# 'EVTokenContract.sol:EVToken', 'EVTokenContract.sol:SafeMath', 
# 'ObjectAttributeContract.sol:ObjectAttribute', 'PolicyManagementContract.sol:PolicyManagement', 
# 'SubjectAttributeContract.sol:SubjectAttribute'])

# print(compiled_sol['SubjectAttributeContract.sol:SubjectAttribute'].keys())
# RESULT:
# 'abi', 'asm', 'bin', 'bin-runtime', 'devdoc', 'function-debug', 
# 'function-debug-runtime', 'generated-sources', 'generated-sources-runtime', 
# 'hashes', 'metadata', 'opcodes', 'srcmap', 'srcmap-runtime', 'storage-layout',
# 'userdoc', 'ast'

# Connecting to Ganache Network
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer = 0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

# set first account as default user or "Administrator"
w3.eth.default_account = ADDR

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
# ----------------------------------------CONTINUE FROM HERE-----------------------------------------
# Check to see if connected to ganache
if w3.isConnected():
    print('[CONNECTED] Goerli Ethereum Test Network Connection Established!')
    
# Get user input for initial balance of EVToken
num_token = int(input('Please Enter the Total Supply of EVToken: '))
print()

CONTRACT_NAME = []
ABI = []
BYTECODE = []
CONTRACT_ADDRESS = []

nonce -= 1
for name in compiled_sol.keys():
    # Skip Access Control because it needs to be deployed at the end
    if (name.split(':')[1] == 'AccessControl' or 
        name.split(':')[1] == 'EVToken' or 
        name.split(':')[1] == 'SafeMath'):
        continue
    # add contract name to contract_name list
    CONTRACT_NAME.append(name.split(':')[1])
    print(f"[DEPLOYING] Deploying {CONTRACT_NAME[-1]}...")
    
    # Get the ABI for the contract
    abi = compiled_sol[name]['abi']
    # Store the ABI for the contract in ABI List
    ABI.append(abi)
    # Get the Bytecode for the contract
    bytecode = compiled_sol[name]['bin']
    # Store the Bytecode in BYTECODE List
    BYTECODE.append(bytecode)
    
    # Create the Contract
    Contract = w3.eth.contract(abi = abi, bytecode = bytecode)
    # Update nonce value
    nonce += 1
    tr['nonce'] = Web3.toHex(nonce)
    # Build Constructor Transaction
    txn = Contract.constructor().buildTransaction(tr)
    # Sign the transaction
    signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    # Send raw transaction
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract = w3.eth.contract(
        address = tx_receipt.contractAddress,
        abi = abi
    )
    
    # Add address to CONTRACT_ADDRESS list
    CONTRACT_ADDRESS.append(tx_receipt.contractAddress)
    print(f"[SUCCESS] {name.split(':')[1]} Successfully Deployed!!!")
    print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")

# Deploy EVToken Contract
for name in compiled_sol.keys():
    # Find EVToken Contract
    if name.split(':')[1] != 'EVToken':
        continue
    
    # Add contract to CONTRACT_NAME
    CONTRACT_NAME.append(name.split(':')[1])
    print(f"[DEPLOYING] Deploying {CONTRACT_NAME[-1]}...")
    
    # Get the ABI for the contract
    abi = compiled_sol[name]['abi']
    # Store the ABI for the contract in ABI List
    ABI.append(abi)
    # Get the Bytecode for the contract
    bytecode = compiled_sol[name]['bin']
    # Store the Bytecode in BYTECODE List
    BYTECODE.append(bytecode)
    
    # Create the Contract
    Contract = w3.eth.contract(abi = abi, bytecode = bytecode)
    # Update nonce value
    nonce += 1
    tr['nonce'] = Web3.toHex(nonce)
    # Build Constructor Transaction
    txn = Contract.constructor(num_token).buildTransaction(tr)
    # Sign the transaction
    signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    # Send raw transaction
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract = w3.eth.contract(
        address = tx_receipt.contractAddress,
        abi = abi
    )
    
    # Add address to CONTRACT_ADDRESS list
    CONTRACT_ADDRESS.append(tx_receipt.contractAddress)
    print(f"[SUCCESS] {name.split(':')[1]} Successfully Deployed!!!")
    print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")

# Deploy Access Control Contract
# Getting the Dictionary key for access control
for name in compiled_sol.keys():
    if 'AccessControl' in name:
        contract_name = name
        break
    
# Append Contract Name into list
CONTRACT_NAME.append(contract_name.split(':')[1])

# Getting abi and bytecode for access control
access_abi = compiled_sol[contract_name]['abi']
access_bytecode = compiled_sol[contract_name]['bin']

# Append contract abi and bytecode into respective lists
ABI.append(access_abi)
BYTECODE.append(access_bytecode)

print(f'[DEPLOYING] Deploying {CONTRACT_NAME[-1]}...')

# Creating the access control contract
Access_Contract = w3.eth.contract(abi = access_abi,
                                  bytecode = access_bytecode)
# Update nonce value
nonce += 1
tr['nonce'] = Web3.toHex(nonce)
# Build Constructor Transaction
txn = Access_Contract.constructor(
    CONTRACT_ADDRESS[2],
    CONTRACT_ADDRESS[0],
    CONTRACT_ADDRESS[1],
    CONTRACT_ADDRESS[3]).buildTransaction(tr)
# Sign the transaction
signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
# Send raw transaction
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

access_contract = w3.eth.contract(
    address = tx_receipt.contractAddress,
    abi = access_abi
)

CONTRACT_ADDRESS.append(tx_receipt.contractAddress)
print(f"[SUCCESS] {CONTRACT_NAME[-1]} Successfully Deployed!!!")
print(f"[INFO] Contract Address: {CONTRACT_ADDRESS[-1]}\n")

try:
    folder = 'Info'
    print(f"[CREATING] Folder called '{folder}'")
    os.mkdir(folder)
except FileExistsError as err:
    print(f'[ERROR] {folder} already exists!')
    print(f'{err}\n')
    

# Save Contract Info
for index, name in enumerate(CONTRACT_NAME):
    print(f'[SAVING] {name}')
    with open(f'Info/{name}.contract', 'w') as file_object:
        file_object.write(CONTRACT_ADDRESS[index])
        file_object.write('\n')
        file_object.write(json.dumps(ABI[index]))
    print(f'[SUCCESS]{name} Information Saved...\n')