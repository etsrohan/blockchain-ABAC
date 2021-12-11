# Import Modules/Functions
import web3
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

sub_id = int(input('Please select the subject account: '))
obj_id = int(input('Please select the object account: '))
sub_addr = w3.eth.accounts[sub_id + 1]
obj_addr = w3.eth.accounts[obj_id + 6]
action = int(input('Please enter the action you want to perform: '))
location = input('Please enter your location: ')
attrib_list = ['' for _ in range(6)]
attrib_list[1] = location

# set default account to manufacturer
w3.eth.default_account = w3.eth.accounts[11]

try:
    tx_hash = subject_contract.functions.change_attribs(sub_addr, attrib_list).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f'Sent change location request for subject: {sub_addr[-4:]}')
except Exception as err:
        print(f'''[ERROR] Subject with address ({sub_addr[-4:]}) does not exist.\n{err}
              \n\rOr Make sure you have permissions to change attributes.''')

# set default account as access sender
w3.eth.default_account = sub_addr

tx_hash = access_contract.functions.access_control(obj_addr, action).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f'Sent Access Request for sub_addr: {sub_addr[-4:]} obj_addr: {obj_addr[-4:]} and action: {action}')