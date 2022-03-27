"""
This file is used to store different functions that will be useful to the functionality
of the ABAC Blockchain system.
"""
from solcx import compile_files
import json
import os
from web3 import Web3
import threading


class BloomACCRunner:
    """
    This class contains several methods and variables that help in the following functionality
    for the ABAC Blockchain Project:
    Functionality:
    1) Deploy system
    2) Connect to existing (deployed) system
    3) Add subjects (from pre-existing set)
    4) Add objects (from pre-existing set)
    5) Add policies (from pre-existing set)
    6) Request access
    """

    # Class Variables
    GANACHE_URL = "HTTP://127.0.0.1:7545"
    CHAIN_ID = 1337

    def __init__(self) -> None:
        # Instance Variables
        self.w3 = None

        # Access Control Contract Variables
        self.acc_address = None
        self.acc_abi = None
        self.acc_contract = None

        # EVToken Contract Variables
        self.evtoken_address = None
        self.evtoken_abi = None
        self.evtoken_contract = None

        # Object Attribute Contract Variables
        self.oac_address = None
        self.oac_abi = None
        self.oac_contract = None

        # Policy Management Contract Variables
        self.pmc_address = None
        self.pmc_abi = None
        self.pmc_contract = None

        # Subject Attribute Contract Variables
        self.sac_address = None
        self.sac_abi = None
        self.sac_contract = None

        # Important Player Addresses
        self.admin = None
        self.cs_leader = []
        self.ev_manufacturer = []
        self.subjects = []
        self.objects = []

    def deploy_bloomacc(self) -> None:
        """Compiles, deploys and saves the access control, subject/object attribute,
        policy management, ev token contracts on a local ganache blockchain
        contract .sol files located in the 'contract' folder."""

        # Compiling the contracts
        cwd = os.getcwd()
        compiled_sol = compile_files(
            [cwd + "/Contracts/AccessControlContract.sol"], solc_version="0.8.7"
        )

        # Create web3 instance
        self.w3 = Web3(Web3.HTTPProvider(self.GANACHE_URL))
        if self.w3.isConnected():
            print("\n[SUCCESS] Connected to the Ganache Instance...\n")
        else:
            print("\n[FAILURE] Error connecting to Ganache Instance...\n")
            return

        # Get total supply of token
        num_token = int(input("Please Enter the Total Supply of EVToken: "))
        self.admin = self.w3.eth.accounts[0]
        # Add EV Manufacturers and CS Leaders
        try:
            self.ev_manufacturer.append(self.w3.eth.accounts[11])
            self.ev_manufacturer.append(self.w3.eth.accounts[12])
            self.cs_leader.append(self.w3.eth.accounts[13])
        except Exception:
            print("[ERROR] Make sure there are at least 14 accounts in Ganache...")
            exit()
        # Add subjects and objects addresses
        for address in self.w3.eth.accounts[1:6]:
            self.subjects.append(address)
        for address in self.w3.eth.accounts[6:11]:
            self.objects.append(address)
        nonce = self.w3.eth.get_transaction_count(self.admin)

        nonce -= 1
        # Deploy PMC, SAC, OAC
        for name in compiled_sol.keys():
            # Skip ACC, EVToken and SafeMath
            short_name = name.split(":")[-1]
            if (
                short_name == "AccessControl"
                or short_name == "EVToken"
                or short_name == "SafeMath"
            ):
                continue

            print(f"[DEPLOYING] {short_name}")

            # ABI
            abi = compiled_sol[name]["abi"]
            # Bytecode
            bytecode = compiled_sol[name]["bin"]

            # Create contract instance
            contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

            # Submit the transaction to deploy the contracts
            nonce += 1
            tx_hash = contract.constructor().transact(
                {"chainId": self.CHAIN_ID, "from": self.admin, "nonce": nonce}
            )
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            contract = self.w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

            if short_name == "SubjectAttribute":
                self.sac_abi = abi
                self.sac_address = tx_receipt.contractAddress
                self.sac_contract = contract
            elif short_name == "ObjectAttribute":
                self.oac_abi = abi
                self.oac_address = tx_receipt.contractAddress
                self.oac_contract = contract
            else:
                self.pmc_abi = abi
                self.pmc_address = tx_receipt.contractAddress
                self.pmc_contract = contract

            print(f"[SUCCESS] {short_name} Successfully Deployed!!!")
            print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")

        # Deploy EVToken Contract
        for name in compiled_sol.keys():
            # Find EVToken Contract
            short_name = name.split(":")[-1]
            if short_name != "EVToken":
                continue

            print(f"[DEPLOYING] {short_name}")

            abi = compiled_sol[name]["abi"]
            bytecode = compiled_sol[name]["bin"]
            contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

            # Deploy
            nonce += 1
            tx_hash = contract.constructor(num_token).transact(
                {"chainId": self.CHAIN_ID, "from": self.admin, "nonce": nonce}
            )
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            contract = self.w3.eth.contract(abi=abi, address=tx_receipt.contractAddress)

            self.evtoken_abi = abi
            self.evtoken_address = tx_receipt.contractAddress
            self.evtoken_contract = contract

            print(f"[SUCCESS] {short_name} Successfully Deployed!!!")
            print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")

        # Deploy Access Control Contract
        for name in compiled_sol.keys():
            short_name = name.split(":")[-1]
            if short_name == "AccessControl":
                break

        print(f"[DEPLOYING] {short_name}")
        abi = compiled_sol[name]["abi"]
        bytecode = compiled_sol[name]["bin"]
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        # Deploy
        nonce += 1
        tx_hash = contract.constructor(
            self.sac_address, self.oac_address, self.pmc_address, self.evtoken_address
        ).transact({"chainId": self.CHAIN_ID, "from": self.admin, "nonce": nonce})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        contract = self.w3.eth.contract(abi=abi, address=tx_receipt.contractAddress)

        self.acc_abi = abi
        self.acc_address = tx_receipt.contractAddress
        self.acc_contract = contract

        print(f"[SUCCESS] {short_name} Successfully Deployed!!!")
        print(f"[INFO] Contract Address: {tx_receipt.contractAddress}\n")

        try:
            folder = "Info"
            print(f"[CREATING] Folder called '{folder}'")
            os.mkdir(folder)
        except FileExistsError as err:
            print(f"[ERROR] {folder} already exists!")
            print(f"{err}\n")

        # Save Contract Info
        # ACC
        print("[SAVING] Contracts...")
        with open("./Info/AccessControl.contract", "w") as file:
            file.write(self.acc_address)
            file.write("\n")
            file.write(json.dumps(self.acc_abi))

        with open("./Info/EVToken.contract", "w") as file:
            file.write(self.evtoken_address)
            file.write("\n")
            file.write(json.dumps(self.evtoken_abi))

        with open("./Info/ObjectAttribute.contract", "w") as file:
            file.write(self.oac_address)
            file.write("\n")
            file.write(json.dumps(self.oac_abi))

        with open("./Info/PolicyManagement.contract", "w") as file:
            file.write(self.pmc_address)
            file.write("\n")
            file.write(json.dumps(self.pmc_abi))

        with open("./Info/SubjectAttribute.contract", "w") as file:
            file.write(self.sac_address)
            file.write("\n")
            file.write(json.dumps(self.sac_abi))

        self.set_access_token()
        self.add_cs_leader()
        self.add_ev_manufacturer()

    def connect_bloomacc(self) -> None:
        """Connect to an already existing and deployed ABAC system"""
        # Setting web3 instance
        self.w3 = Web3(Web3.HTTPProvider(self.GANACHE_URL))

        if self.w3.isConnected():
            print("\n[SUCCESS] Connected to Ganache instance...")
        else:
            print("\n[FAILURE] Error connecting to Ganache instance...")
            return

        # Setting player addresses
        print("[PROCESSING] Setting players...")
        self.admin = self.w3.eth.accounts[0]
        # Clear all the lists
        self.ev_manufacturer = []
        self.cs_leader = []
        self.subjects = []
        self.objects = []
        try:
            self.ev_manufacturer.append(self.w3.eth.accounts[11])
            self.ev_manufacturer.append(self.w3.eth.accounts[12])
            self.cs_leader.append(self.w3.eth.accounts[13])
        except Exception:
            print("[ERROR] Make sure there are at least 14 accounts in Ganache...")
            exit()
        for address in self.w3.eth.accounts[1:6]:
            self.subjects.append(address)
        for address in self.w3.eth.accounts[6:11]:
            self.objects.append(address)

        # Contract info
        # ACC
        print("[PROCESSING] Accessing contract info...")
        try:
            with open("./Info/AccessControl.contract", "r") as file:
                info = file.readlines()
                self.acc_address = info[0][:-1]
                self.acc_abi = json.loads(info[1])

            with open("./Info/SubjectAttribute.contract", "r") as file:
                info = file.readlines()
                self.sac_address = info[0][:-1]
                self.sac_abi = json.loads(info[1])

            with open("./Info/ObjectAttribute.contract", "r") as file:
                info = file.readlines()
                self.oac_address = info[0][:-1]
                self.oac_abi = json.loads(info[1])

            with open("./Info/PolicyManagement.contract", "r") as file:
                info = file.readlines()
                self.pmc_address = info[0][:-1]
                self.pmc_abi = json.loads(info[1])

            with open("./Info/EVToken.contract", "r") as file:
                info = file.readlines()
                self.evtoken_address = info[0][:-1]
                self.evtoken_abi = json.loads(info[1])
        except Exception:
            print("The files you are looking for are not here...")
            exit()

        # Contract objects
        print("[PROCESSING] Creating contract objects...")
        self.acc_contract = self.w3.eth.contract(
            address=self.acc_address, abi=self.acc_abi
        )

        self.sac_contract = self.w3.eth.contract(
            address=self.sac_address, abi=self.sac_abi
        )

        self.oac_contract = self.w3.eth.contract(
            address=self.oac_address, abi=self.oac_abi
        )

        self.pmc_contract = self.w3.eth.contract(
            address=self.pmc_address, abi=self.pmc_abi
        )

        self.evtoken_contract = self.w3.eth.contract(
            address=self.evtoken_address, abi=self.evtoken_abi
        )
        print("[SUCCESS] Connected to deployed network...")

    def set_access_token(self) -> None:
        """Sets access control contract address in EVToken Contract"""
        print("[ADMIN] Connecting ACC to EVToken...")
        nonce = self.w3.eth.get_transaction_count(self.admin)
        tx_hash = self.evtoken_contract.functions.set_access_address(
            self.acc_address
        ).transact({"chainId": self.CHAIN_ID, "from": self.admin, "nonce": nonce})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def add_cs_leader(self) -> None:
        """Adds predefined CS Leaders who can then add CS stations (Objects)"""
        nonce = self.w3.eth.get_transaction_count(self.admin)
        nonce -= 1
        for address in self.cs_leader:
            print(f"[ADMIN] Adding CS Leader 0x...{address[-4:]}")
            nonce += 1
            tx_hash = self.oac_contract.functions.add_cs_leader(address).transact(
                {"chainId": self.CHAIN_ID, "from": self.admin, "nonce": nonce}
            )
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def add_ev_manufacturer(self) -> None:
        """Adds predefined EV Manufacturers that can add more Electric Vehicles (Subjects)"""
        nonce = self.w3.eth.get_transaction_count(self.admin)
        nonce -= 1
        for address in self.ev_manufacturer:
            nonce += 1
            print(f"[ADMIN] Adding EV Manufacturer 0x...{address[-4:]}")
            tx_hash = self.sac_contract.functions.add_ev_man(address).transact(
                {"chainId": self.CHAIN_ID, "from": self.admin, "nonce": nonce}
            )
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def add_subject(self) -> None:
        """EV Manufacturers adding EVs into the environment
        Subject Attributes:
          Manufacturer, Current Location, Vehicle Type, Owner Name
          License Plate Number, Energy Capacity, ToMFR"""
        # Get subject info
        with open("./Attributes/subjects.txt", "r") as file:
            sub_info = file.readlines()
        print()
        # Create and start new threads for every subject
        threads = []
        for index, info in enumerate(sub_info):
            # Remove \n from end of each string
            if info[-1] == "\n":
                info = info[:-1]
            thread = threading.Thread(
                target=self.send_subject,
                args=(
                    self.subjects[index],
                    info,
                    self.ev_manufacturer[-1],
                ),
            )
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        # Call subjects abi to confirm that subjects were added successfully
        for address in self.subjects:
            print(f"Subject: {self.sac_contract.functions.subjects(address).call()}")
        print("\n[ADD SUBJECTS][SUCCESS] Transactions Successful\n")

    def send_subject(self, sub_addr, info, ev_man) -> None:
        """A helper function to send transaction for adding a new subject"""
        try:
            tx_hash = self.sac_contract.functions.subject_add(
                sub_addr, info.split(";")
            ).transact({"chainId": self.CHAIN_ID, "from": ev_man})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"[SUCCESS] Added subject {info.split(';')[0]}")
        except Exception as err:
            print(err)
            print("[ERROR] Remember to add EV Manufacturers to Subject Contract!")

    def add_object(self) -> None:
        """CS Leaders adding Charging Stations into the environment
        Object Attributes:
          Plug Type, Location, Pricing Model, Number of Charging Outlets
          Charging Power, Fast Charging"""
        # Get object info
        with open("./Attributes/objects.txt", "r") as file:
            obj_info = file.readlines()
        print()
        # Create and start new threads for every object
        threads = []
        for index, info in enumerate(obj_info):
            # Remove \n from end of each string
            if info[-1] == "\n":
                info = info[:-1]
            thread = threading.Thread(
                target=self.send_object,
                args=(
                    self.objects[index],
                    info,
                    self.cs_leader[-1],
                ),
            )
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        # Call objects abi to confirm that objects were added successfully
        for address in self.objects:
            print(f"Object: {self.oac_contract.functions.objects(address).call()}")
        print("\n[ADD OBJECTS][SUCCESS] Transactions Successful\n")

    def send_object(self, obj_addr, info, cs_lead) -> None:
        """A helper function to send transaction for adding a new object"""
        try:
            tx_hash = self.oac_contract.functions.object_add(
                obj_addr, info.split(";")
            ).transact({"chainId": self.CHAIN_ID, "from": cs_lead})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"[SUCCESS] Added object {info.split(';')[1]}")
        except Exception as err:
            print(err)
            print("[ERROR] Remember to add CS Leaders to Object Contract!")

    def add_policy(self) -> None:
        """Admin adding policies that control which subject can access what object.
        Policy Content:
        Subject = (Manufacturer, Current Location, Vehicle Type, Owner Name, License Plate Number, Energy Capacity, ToMFR)
        Object = (Plug Type, Location, Pricing Model, Number of Charging Outlets, Charging Power, Fast Charging)
        Action = (read, write, execute)
        Context = (min_interval, start_time, end_time)
        policy_add ABI expects 4 inputs: subject list, object list, action list, context list"""
        # Get policy info
        with open("./Attributes/policies.txt", "r") as file:
            policy_info = file.readlines()

        print()
        threads = []
        for policy in policy_info:
            # Remove '\n' from end
            if policy[-1] == "\n":
                policy = policy[:-1]
            thread = threading.Thread(
                target=self.send_policy,
                args=(policy,),
            )
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        # Check if every policy was successfully added
        for i in range(len(policy_info)):
            print(f"Policy:\n{self.pmc_contract.functions.get_policy(i).call()}")
        print("\n[ADD POLICY][SUCCESS] Transactions Successful\n")

    def send_policy(self, policy) -> None:
        """A helper function to add new policies to the PMC"""
        # Split policy into subject, object, action, context
        policy = policy.split(":")
        if len(policy) != 4:
            print("[ERROR] INVALID POLICY. MAKE SURE POLICY HAS 4 PARTS.")
            return

        for i in range(4):
            policy[i] = policy[i].split(";")

        # Loop through every action and turn it into a boolean
        for i in range(3):
            if policy[2][i].lower() == "true":
                policy[2][i] = True
            else:
                policy[2][i] = False

        # Convert context into list of 3 ints
        for i in range(3):
            policy[3][i] = int(policy[3][i])

        # Send tx
        tx_hash = self.pmc_contract.functions.policy_add(*policy).transact(
            {"chainId": self.CHAIN_ID, "from": self.admin}
        )
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(
            f"""[SUCCESS] Added policy\n
              \r\t{policy[0]}\n
              \r\t{policy[1]}\n
              \r\t{policy[2]}\n
              \r\t{policy[3]}\n"""
        )

    def access_control(self) -> None:
        """A method to get subject/object/action information and current location to call access control abi.
        Access control ABI:
        sub_id, obj_id, action all are ints
               Subject Attributes:
          Manufacturer, current_location, vehicle_type, charging_efficiency
          discharging_efficiency, energy_capacity, ToMFR"""
        sub_addr = input("Please enter the subject address: ")
        obj_addr = input("Please enter the object address: ")
        action = int(input("Please select the action you want to perform: "))
        location = input("Please enter your location: ")
        attrib_list = ["" for i in range(6)]
        attrib_list[1] = location

        nonce = self.w3.eth.get_transaction_count(self.ev_manufacturer[-1])
        try:
            tx_hash = self.sac_contract.functions.change_attribs(
                sub_addr, attrib_list
            ).transact(
                {
                    "chainId": self.CHAIN_ID,
                    "from": self.ev_manufacturer[-1],
                    "nonce": nonce,
                }
            )
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Sent current location...")
        except Exception as err:
            print(
                f"""[ERROR] Subject with address (0x...{sub_addr[-4:]}) does not exist.\n{err}
                \n\rOr make sure you have permissions to change attributes..."""
            )

        nonce = self.w3.eth.get_transaction_count(sub_addr)
        tx_hash = self.acc_contract.functions.access_control(obj_addr, action).transact(
            {
                "chainId": self.CHAIN_ID,
                "from": sub_addr,
                "nonce": nonce,
            }
        )
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(
            f"Sent access request for subject address: 0x...{sub_addr[-4:]}, object address: 0x...{obj_addr[-4:]} and action: {action}"
        )
