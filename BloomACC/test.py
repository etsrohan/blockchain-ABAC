# Import Modules/Functions
from web3 import Web3
import threading
import json

# Connect to Ganache
GANACHE_URL = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GANACHE NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = w3.eth.accounts[0]

with open('SubjectAttribute.contract', 'r') as file_obj:
    subject_info = file_obj.readlines()

# print(subject_info)
# Gives a list of adderss and abi
# Get address/abi for subject contract
subject_address = subject_info[0][:-1]
subject_abi = json.loads(subject_info[1])

# Connecting to subject contract
subject_contract = w3.eth.contract(
    address = subject_address,
    abi = subject_abi
)

# --------------------------MAIN PROGRAM----------------------------
# Subject Attributes:
#   Manufacturer, current_location, vehicle_type, charging_efficiency
#   discharging_efficiency, energy_capacity, ToMFR

sub_id = int(input('Please enter your subject id: '))
location = input('Please enter your location: ')
attrib_list = ['' for _ in range(6)]
attrib_list[1] = location

tx_hash = subject_contract.functions.change_attribs(sub_id, attrib_list).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f'''Subject attributes:
      \r\t{subject_contract.functions.subjects(sub_id).call()}''')