// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract ObjectAttribute {
    // ENUMS
    enum ObjectState {NotCreated, Active, Suspended, Deactivated}

    // STRUCTS
    struct Object{
        ObjectState state;
        string name;
        string organization;
        string department;
        string lab;
        string place;
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
    modifier obj_active(uint256 obj_id){
        require(objects[obj_id].state == ObjectState.Active);
        _;
    }
    modifier obj_not_deactivated(uint256 obj_id){
        require(objects[obj_id].state != ObjectState.Deactivated);
        _;
    }

    // EVENTS
    event NewObjectAdded(uint256 obj_id);
    event ObjectChanged(uint256 obj_id);

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
    }

    function object_add(
        string[] memory obj_arg
        /*ADD ARGUMENTS*/
    )
        public
        admin_only()
    {
        uint256 obj_id = num_objects;
        num_objects++;
        objects[obj_id].state = ObjectState.Active;
        // ADD MAIN ATTRIBS
        objects[obj_id].name = obj_arg[0];
        objects[obj_id].organization = obj_arg[1];
        objects[obj_id].department = obj_arg[2];
        objects[obj_id].lab = obj_arg[3];
        objects[obj_id].place = obj_arg[4];
        objects[obj_id].other = obj_arg[5];
    }

    function delete_object(
        uint256 obj_id
    )
        public
        admin_only()
        obj_not_deactivated(obj_id)
    {
        objects[obj_id].state = ObjectState.Deactivated;
    }

    function suspend_object(
        uint256 obj_id
    )
        public
        admin_only()
        obj_not_deactivated(obj_id)
    {
        objects[obj_id].state = ObjectState.Suspended;
    }

    function change_attribs(
        uint256 obj_id,
        string[] memory obj_arg
    )
        public
        admin_only()
        obj_active(obj_id)
    {
        // CHANGE MAIN ATTRIBS
        // Check for empty field, if empty don't change
        bytes memory empty_test = bytes(obj_arg[0]);
        if (empty_test.length != 0) objects[obj_id].name = obj_arg[0];
        empty_test = bytes(obj_arg[1]);
        if (empty_test.length != 0) objects[obj_id].organization = obj_arg[1];
        empty_test = bytes(obj_arg[2]);
        if (empty_test.length != 0) objects[obj_id].department = obj_arg[2];
        empty_test = bytes(obj_arg[3]);
        if (empty_test.length != 0) objects[obj_id].lab = obj_arg[3];
        empty_test = bytes(obj_arg[4]);
        if (empty_test.length != 0) objects[obj_id].place = obj_arg[4];
        empty_test = bytes(obj_arg[5]);
        if (empty_test.length != 0) objects[obj_id].other = obj_arg[5];

        // Emit event for successful object attribute change 
        emit ObjectChanged(obj_id);
    }
}