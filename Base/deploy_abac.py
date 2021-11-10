from eth_typing.ethpm import ContractName
from solcx import compile_files, compile_source
import os
from web3 import Web3
import json

from web3._utils.blocks import is_predefined_block_number

# Getting current working directory (cwd)
cwd = os.getcwd()
# Compile ABAC Contracts
compiled_sol = compile_files([cwd + '/AccessControlContract.sol'])

# Some important exploration
# print(os.getcwd())
# /home/rohan/Desktop/Blockchain-ABAC/Base

# print(compiled_sol.keys())
# '/home/rohan/Desktop/Blockchain-ABAC/Base/AccessControlContract.sol:AccessControl', 
# 'ObjectAttributeContract.sol:ObjectAttribute', 'PolicyManagementContract.sol:PolicyManagement', 
# 'SubjectAttributeContract.sol:SubjectAttribute'

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
    if 'AccessControl' in name:
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
    
    # Create the Subject Contract
    SubjectContract = w3.eth.contract(abi = abi, bytecode = bytecode)
    # submit transaction that deploys the contract
    tx_hash = SubjectContract.constructor().transact()
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
CONTRACT_NAME = tuple(CONTRACT_NAME)
ABI = tuple(ABI)
BYTECODE = tuple(BYTECODE)
CONTRACT_ADDRESS = tuple(CONTRACT_ADDRESS)

for index in range(3):
    print(f'[SAVING] {CONTRACT_NAME[index]}')
    with open(f'{CONTRACT_NAME[index]}.contract', 'w') as file_object:
        file_object.write(CONTRACT_ADDRESS[index])
        file_object.write('\n')
        file_object.write(json.dumps(ABI[index]))
    print(f'[SUCCESS]{CONTRACT_NAME[index]} Information Saved...\n')

# Deploy Access Control Contract
