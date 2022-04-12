# Import Modules and Functions
from solcx import compile_files, compile_source
import os
from web3 import Web3
import json

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
ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Check to see if connected to ganache
if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')
    
# Get user input for initial balance of EVToken
num_token = int(input('Please Enter the Total Supply of EVToken:'))
print()

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

CONTRACT_NAME = []
ABI = []
BYTECODE = []
CONTRACT_ADDRESS = []
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
    # submit transaction that deploys the contract
    tx_hash = Contract.constructor().transact()
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
    # submit transaction that deploys the contract
    tx_hash = Contract.constructor(num_token).transact()
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
# Transact the constructor
tx_hash = Access_Contract.constructor(
    CONTRACT_ADDRESS[2],
    CONTRACT_ADDRESS[0],
    CONTRACT_ADDRESS[1],
    CONTRACT_ADDRESS[3]).transact()
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