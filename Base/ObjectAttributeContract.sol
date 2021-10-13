// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract ObjectAttribute {
    // ENUMS
    enum ObjectState {NotCreated, Active, Deactivated}

    // STRUCTS
    struct Object{
        ObjectState state;
        string name;
        string organization;
        string department;
        string lab;
        string role;
        string other;
    }

    // VARIABLES
    address admin;
    uint256 num_objects;

    mapping (uint256 => Object) public objects;

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }

    // EVENTS
    event NewObjectAdded(uint256 sub_id);

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
    }

    function object_add(
        string memory sub_name
        /*ADD ARGUMENTS*/
    )
        public
        admin_only()
    {
        uint256 obj_id = num_objects;
        num_objects++;
        objects[obj_id].state = ObjectState.Active;
        // ADD OTHER ATTRIBS
        objects[obj_id].name = sub_name;
    }

    function delete_object(
        uint256 obj_id
    )
        public
        admin_only()
    {
        objects[obj_id].state = ObjectState.Deactivated;
    }

    // function change_attribs(uint256 obj_id)
}