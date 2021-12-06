# Import Modules/Functions
from web3 import Web3
import json

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# Open and get Access ABI/Address
with open('AccessControl.contract', 'r') as file_obj:
    access_info = file_obj.readlines()
# Open and get SubjectContract ABI/Address
with open('SubjectAttribute.contract', 'r') as file_obj:
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
# --------------------------MAIN PROGRAM----------------------------
# Access control ABI:
# sub_id, obj_id, action all are ints

# Subject Attributes:
#   Manufacturer, current_location, vehicle_type, charging_efficiency
#   discharging_efficiency, energy_capacity, ToMFR

sub_id = int(input('Please enter your sub_id: '))
obj_id = int(input('Please enter the obj_id: '))
action = int(input('Please enter the action you want to perform: '))
location = input('Please enter your location: ')
attrib_list = ['' for _ in range(6)]
attrib_list[1] = location

# set default account as admin
w3.eth.default_account = w3.eth.accounts[0]

tx_hash = subject_contract.functions.change_attribs(sub_id, attrib_list).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Sent change location request for subject: {sub_id}')

# set default account as access sender
w3.eth.default_account = w3.eth.accounts[sub_id + 1]

tx_hash = access_contract.functions.access_control(sub_id, obj_id, action).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Sent Access Request for sub_id: {sub_id} obj_id: {obj_id} and action: {action}')