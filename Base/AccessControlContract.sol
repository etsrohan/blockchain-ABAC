// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import 'PolicyManagementContract.sol';
import 'SubjectAttributeContract.sol';
import 'ObjectAttributeContract.sol';

contract AccessControl {
    // VARIABLES
    address policy_address;
    address subject_address;
    address object_address;
    address admin;

    // EVENTS

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
        view
        returns (bool)
    {
        // Subject Information
        SubjectAttribute subject_contract = SubjectAttribute(subject_address);
        SubjectAttribute.SubjectState sub_state;
        string[] memory sub_arg;
        (sub_state, sub_arg[0], sub_arg[1], sub_arg[2], sub_arg[3], sub_arg[4], sub_arg[5]) = subject_contract.subjects(sub_id);

        // Object Information
        ObjectAttribute object_contract = ObjectAttribute(object_address);
        ObjectAttribute.ObjectState obj_state;
        string[] memory obj_arg;
        (obj_state, obj_arg[0], obj_arg[1], obj_arg[2], obj_arg[3], obj_arg[4], obj_arg[5]) = object_contract.objects(obj_id);

        return true;
    }
}