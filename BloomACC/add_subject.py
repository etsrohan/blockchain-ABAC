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

# Send subject function to send subject_add transaction
def send_subject(address, subject):
    """
    Function which is used as a target for threading to send
    transactions to add new subjects to SubjectAttributeContract
    """
    tx_hash = subject_contract.functions.subject_add(address, subject.split(';')).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[SUCCESS] Added subject {subject.split(';')[0]}")

# Get subjects data from subjects.txt
with open('subjects.txt', 'r') as file_obj:
    sub_info = file_obj.readlines()

# For every subject in sub_info send subject_add transaction 
threads = []
for index, subject in enumerate(sub_info):
    # Remove \n at the end of each string if it exists
    if subject[-1] == '\n':
        subject = subject[:-1]
    # Create a new thread for every subject
    thread = threading.Thread(
        target = send_subject,
        args = (w3.eth.accounts[1 + index], subject)
    )
    # Add thread to threads list 
    threads.append(thread)
# Start the threads in threads list
for thread in threads:
    thread.start()
# Wait for threads to finish before calling subjects
for thread in threads:
    thread.join()
# Call subjects abi to confirm that every subject was added successfully.
for address in w3.eth.accounts[1:6]:
    print('Subject:\n\t', subject_contract.functions.subjects(address).call())
print('\n[ADD SUBJECTS][SUCCESS] Transactions Successful\n')