# Import Modules/Functions
from web3 import Web3, middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json

subject_address_list = [
    "0x6a09436F3Cb7C3e871071033ABA967327499b9d4",
    "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a",
    "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B",
    "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23",
    "0xa72e420605FD940b860c493263ce891d434782CB"
]

# Global Variables
ADDR = "0xD5956cfB4Bb948ADcE1033580b85257C624c29d7"
PRIVATE_KEY = "8feaed78e867d6aebd5bab7c5f835b25a0f17b7f191316d16650e63d9bd16ecf"
# Connect to Goerli
INFURA_URL = "https://goerli.infura.io/v3/60febbc1f74c4e229c6f6f694ea571ac"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer = 0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

if w3.isConnected():
    print('\n[SUCCESS] CONNECTED TO GOERLI TEST NETWORK\n')

# set first account as default user or "Administrator"
w3.eth.default_account = ADDR

with open('Info/SubjectAttribute.contract', 'r') as file_obj:
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

# Setting Strategy, Nonce, and Gas Price
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

# --------------------------MAIN PROGRAM----------------------------
# Subject Attributes:
#   Manufacturer, Current Location, Vehicle Type, Owner Name
#   License Plate Number, Energy Capacity, ToMFR

# Send subject function to send subject_add transaction
def send_subject(address, subject, tr):
    """
    Function which is used as a target for threading to send
    transactions to add new subjects to SubjectAttributeContract
    """
    try:
        txn = subject_contract.functions.subject_add(address, subject.split(';')).buildTransaction(tr)
        # Sign the transaction
        signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        # Send raw transaction
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        # wait for the transaction to be mined and get the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"[SUCCESS] Added subject {subject.split(';')[0]}")
    except Exception as err:
        print('{ERROR] Remember to add EV Manufacturers to the Subject Contract!')

# Get subjects data from subjects.txt
with open('Attributes/subjects.txt', 'r') as file_obj:
    sub_info = file_obj.readlines()

nonce -= 1
# For every subject in sub_info send subject_add transaction 
for index, sub in enumerate(sub_info):
    # Remove \n at the end of each string if it exists
    if sub[-1] == '\n':
        sub = sub[:-1]
    
    # Update nonce
    nonce += 1
    tr['nonce'] = Web3.toHex(nonce)
    # Send add_subject transaction
    print('\nAdding new Subject')
    send_subject(subject_address_list[index], sub, tr)
    
# Call subjects abi to confirm that every subject was added successfully.
for address in subject_address_list:
    print('Subject:\n\t', subject_contract.functions.subjects(address).call())
print('\n[ADD SUBJECTS][SUCCESS] Transactions Successful\n')