# Import Modules and Functions
from solcx import compile_files, compile_source
import os
from web3 import Web3
import json

# Getting current working directory (cwd)
cwd = os.getcwd()
# Compile ABAC Contracts
compiled_sol = compile_files([cwd + '/AccessControlContract.sol'])

# Some important exploration
# print(os.getcwd())
# /home/rohan/Desktop/Blockchain-ABAC/BloomACC

# print(compiled_sol.keys())
# dict_keys(['/home/rohan/Desktop/Blockchain-ABAC/BloomACC/AccessControlContract.sol:AccessControl', 
# 'EVTokenContract.sol:EVToken', 'EVTokenContract.sol:SafeMath', 
# 'ObjectAttributeContract.sol:ObjectAttribute', 'PolicyManagementContract.sol:PolicyManagement', 
# 'SubjectAttributeContract.sol:SubjectAttribute'])

# print(compiled_sol['SubjectAttributeContract.sol:SubjectAttribute'].keys())
# 'abi', 'asm', 'bin', 'bin-runtime', 'devdoc', 'function-debug', 
# 'function-debug-runtime', 'generated-sources', 'generated-sources-runtime', 
# 'hashes', 'metadata', 'opcodes', 'srcmap', 'srcmap-runtime', 'storage-layout',
# 'userdoc', 'ast'

# Connecting to Ganache Network
ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

CONTRACT_NAME = []
ABI = []
BYTECODE = []
CONTRACT_ADDRESS = []
for name in compiled_sol.keys():
    # Skip Access Control because it needs to be deployed at the end
    if 'AccessControl' in name or 'EVToken' in name:
        continue
    print(f"[DEPLOYING] Deploying {name}...")
    # add contract name to contract_name list
    CONTRACT_NAME.append(name)
    
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
    print(f"[SUCCESS] {name} Successfully Deployed!!!")
    print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")
    
# convert contract_name,  from list to tuple to avoid changing it
# CONTRACT_NAME = tuple(CONTRACT_NAME)
# ABI = tuple(ABI)
# BYTECODE = tuple(BYTECODE)
# CONTRACT_ADDRESS = tuple(CONTRACT_ADDRESS)

for index in range(3):
    if 'Object' in CONTRACT_NAME[index]:
        name = 'ObjectAttribute'
    elif 'Subject' in CONTRACT_NAME[index]:
        name  = 'SubjectAttribute'
    elif 'Policy' in CONTRACT_NAME[index]:
        name = 'PolicyManagement'
    else:
        print(f'[ERROR] {CONTRACT_NAME[index]} name unknown...')
        continue
    
    print(f'[SAVING] {name}')
    with open(f'{name}.contract', 'w') as file_object:
        file_object.write(CONTRACT_ADDRESS[index])
        file_object.write('\n')
        file_object.write(json.dumps(ABI[index]))
    print(f'[SUCCESS]{name} Information Saved...\n')

# Deploy Access Control Contract
# Getting the Dictionary key for access control
for name in compiled_sol.keys():
    if 'AccessControl' in name:
        contract_name = name
        break

# Getting abi and bytecode for access control
access_abi = compiled_sol[name]['abi']
access_bytecode = compiled_sol[name]['bin']
print(f'[DEPLOYING] Deploying Access Control Contract...')

# Creating the access control contract
Access_Contract = w3.eth.contract(abi = access_abi,
                                  bytecode = access_bytecode)
# Transact the constructor
tx_hash = Access_Contract.constructor(CONTRACT_ADDRESS[1], CONTRACT_ADDRESS[2], CONTRACT_ADDRESS[0]).transact()
# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

access_contract = w3.eth.contract(
    address = tx_receipt.contractAddress,
    abi = access_abi
)
print(f"[SUCCESS] Access Control Contract Successfully Deployed!!!")
print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")

print(f'[SAVING] AccessControl')
with open('AccessControl.contract', 'w') as file_object:
    file_object.write(tx_receipt.contractAddress)
    file_object.write('\n')
    file_object.write(json.dumps(access_abi))
print(f'[SUCCESS] AccessControl Information Saved...\n')