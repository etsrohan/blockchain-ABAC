// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import 'PolicyManagementContract.sol';
import 'SubjectAttributeContract.sol';
import 'ObjectAttributeContract.sol';

contract AccessControl {
    // STRUCTS
    struct Store {
        string name;
        string organization;
        string department;
        string lab;
        string role_place;
        string other;
    }

    // VARIABLES
    address policy_address;
    address subject_address;
    address object_address;
    address admin;

    // EVENTS
    event AccessGranted (uint256 sub_id, uint256 obj_id, uint8 action);
    event AccessDenied (uint256 sub_id, uint256 obj_id, uint8 action, string message);

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }

    // FUNCTIONS
    constructor(address pol_con, address sub_con, address obj_con)
    {
        admin = msg.sender;
        policy_address = pol_con;
        subject_address = sub_con;
        object_address = obj_con;
    }


    // Change the Addresses of the Policy/Subject/Object
    // contracts that Access Control calls
    function change_address(
        /**CONTRACT ADDRESSES**/
        address pol,
        address sub,
        address obj
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        policy_address = pol;
        subject_address = sub;
        object_address = obj;
    }

    
    // Main access control function
    // Gets Subject/Object attributes from Subject/Object Contracts
    // Feeds Subject/Object Attributess to Policy Management Contract
    // From all the actions decides whether to allow access to object
    // ACTION: 0 = read, 1 = write, 2 = execute, 3 = read & write, 4 = ...
    // Add more actions in the future
    function access_control(
        /**SUBJECT AND OBJECT IDS**/
        uint256 sub_id,
        uint256 obj_id,
        /**ACTION**/
        uint8 action
    )
        /**MODIFIERS**/
        public
    {
        // Check Bloom Filter for existance of subject
        SubjectAttribute subject_contract = SubjectAttribute(subject_address);
        if(!subject_contract.check_bitmap(sub_id)){
            emit AccessDenied(sub_id, obj_id, action, "Subject Not Found!");
            return;
        }

        // Subject Information
        SubjectAttribute.SubjectState sub_state;
        Store memory sub_arg;
        (sub_state,
         sub_arg.name,
         sub_arg.organization,
         sub_arg.department,
         sub_arg.lab,
         sub_arg.role_place,
         sub_arg.other)
         = subject_contract.subjects(sub_id);

        // Object Information
        ObjectAttribute object_contract = ObjectAttribute(object_address);
        ObjectAttribute.ObjectState obj_state;
        Store memory obj_arg;
        (obj_state,
         obj_arg.name,
         obj_arg.organization,
         obj_arg.department,
         obj_arg.lab,
         obj_arg.role_place,
         obj_arg.other)
         = object_contract.objects(obj_id);
        
        // Send Subject and Object info to Policy Management contract
        // and get list of policies relating to Subject and Object
        PolicyManagement policy_contract = PolicyManagement(policy_address);
        policy_contract.find_match_policy([sub_arg.name,
                                           sub_arg.organization,
                                           sub_arg.department,
                                           sub_arg.lab,
                                           sub_arg.role_place,
                                           sub_arg.other],
                                          [obj_arg.name,
                                           obj_arg.organization,
                                           obj_arg.department,
                                           obj_arg.lab,
                                           obj_arg.role_place,
                                           obj_arg.other]);

        uint256[] memory ret_list = policy_contract.get_ret_list();

        // Function call to check action against list of policies
        // and return yes/no access variable
        bool access = policy_contract.get_access(ret_list, action);

        // Emit AccessGranted or AccessDenied events if subject has 
        // access to that object
        if (access) {
            emit AccessGranted(sub_id, obj_id, action);
        } else {
            emit AccessDenied(sub_id, obj_id, action, "Permission Invalid");
        }
    }
}