// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import 'PolicyManagementContract.sol';
import 'SubjectAttributeContract.sol';
import 'ObjectAttributeContract.sol';
import 'EVTokenContract.sol';

contract AccessControl {
    // STRUCTS
    struct Store {
        string attribute_1;
        string attribute_2;
        string attribute_3;
        string attribute_4;
        string attribute_5;
        string attribute_6;
    }

    // VARIABLES
    address policy_address;
    address subject_address;
    address object_address;
    address token_address;
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
    constructor(address sub_con, address obj_con, address pol_con, address tok_con)
    {
        admin = msg.sender;
        policy_address = pol_con;
        subject_address = sub_con;
        object_address = obj_con;
        token_address = tok_con;
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
    // Checks bloom filter for existance of subject
    // Gets Subject/Object attributes from Subject/Object Contracts
    // Feeds Subject/Object Attributess to Policy Management Contract
    // From all the actions decides whether to allow access to object
    // ACTION: 0 = read, 1 = write, 2 = execute, 3 = read & write, 4 = ...
    // Emits AccessGranted for successful access request
    // Emits AccessDenied with failure message otherwise
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
        uint256 ToMFR;
        (sub_state,
         sub_arg.attribute_1,
         sub_arg.attribute_2,
         sub_arg.attribute_3,
         sub_arg.attribute_4,
         sub_arg.attribute_5,
         sub_arg.attribute_6,
         ToMFR)
         = subject_contract.subjects(sub_id);

        // Object Information
        ObjectAttribute object_contract = ObjectAttribute(object_address);
        ObjectAttribute.ObjectState obj_state;
        Store memory obj_arg;
        (obj_state,
         obj_arg.attribute_1,
         obj_arg.attribute_2,
         obj_arg.attribute_3,
         obj_arg.attribute_4,
         obj_arg.attribute_5,
         obj_arg.attribute_6)
         = object_contract.objects(obj_id);
        
        // Send Subject and Object info to Policy Management contract
        // and get list of policies relating to Subject and Object
        PolicyManagement policy_contract = PolicyManagement(policy_address);
        uint256[] memory ret_list = policy_contract.find_match_policy(
        [sub_arg.attribute_1,
         sub_arg.attribute_2,
         sub_arg.attribute_3,
         sub_arg.attribute_4,
         sub_arg.attribute_5,
         sub_arg.attribute_6],
        [obj_arg.attribute_1,
         obj_arg.attribute_2,
         obj_arg.attribute_3,
         obj_arg.attribute_4,
         obj_arg.attribute_5,
         obj_arg.attribute_6]);

        // Function call to check action against list of policies
        // and return yes/no access variable
        uint8 access = policy_contract.get_access(ret_list, action, ToMFR);

        // Change the Time of Most Frequent Request for subject
        subject_contract.update_tomfr(sub_id);

        // Emit AccessGranted or AccessDenied events if subject has 
        // access to that object depending on error code from get_access function
        if (access == 0) {
            EVToken token_contract = EVToken(token_address);
            token_contract.transfer_from_admin(msg.sender, 1);
            emit AccessGranted(sub_id, obj_id, action);
        } else if (access == 1){
            emit AccessDenied(sub_id, obj_id, action, "No Match Policy");
        } else if (access == 2){
            emit AccessDenied(sub_id, obj_id, action, "Permission Restricted");
        } else if (access == 3){
            emit AccessDenied(sub_id, obj_id, action, "Access Time Out");
        } else if (access == 4){
            emit AccessDenied(sub_id, obj_id, action, "Too Frequent Request");
        }
    }
}