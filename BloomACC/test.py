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
print(os.getcwd())
# /home/rohan/Desktop/Blockchain-ABAC/BloomACC

print(compiled_sol.keys())
# dict_keys(['/home/rohan/Desktop/Blockchain-ABAC/BloomACC/AccessControlContract.sol:AccessControl', 
# 'EVTokenContract.sol:EVToken', 'EVTokenContract.sol:SafeMath', 
# 'ObjectAttributeContract.sol:ObjectAttribute', 'PolicyManagementContract.sol:PolicyManagement', 
# 'SubjectAttributeContract.sol:SubjectAttribute'])
