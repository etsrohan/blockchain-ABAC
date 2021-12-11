// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract ObjectAttribute {
    // ENUMS
    enum ObjectState {NotCreated, Active, Suspended, Deactivated}

    // STRUCTS
    struct Object{
        ObjectState state;
        string plug_type;
        string location;
        string pricing_model;
        string num_charging_outlets;
        string charging_power;
        string fast_charging;
    }

    // VARIABLES
    address admin;
    uint256 num_objects;

    mapping (address => Object) public objects;

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }
    modifier obj_active(address obj_addr){
        require(objects[obj_addr].state == ObjectState.Active);
        _;
    }
    modifier obj_not_deactivated(address obj_addr){
        require(objects[obj_addr].state != ObjectState.Deactivated);
        _;
    }

    // EVENTS
    event NewObjectAdded(address obj_addr, string location);
    event ObjectChanged(address obj_addr);

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
        num_objects = 0;
    }

    // Adds Object with given attributes:
    // avg_wait_time, location, avg_charging_time, num_charging_outlet, charging_power, utilization_rate
    // Emits NewObjectAdded event with obj_addr and location
    function object_add(
        /**OBJECT ATTRIBUTES**/
        address obj_addr,
        string[6] memory obj_arg
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        num_objects++;
        objects[obj_addr].state = ObjectState.Active;
        // ADD MAIN ATTRIBS
        objects[obj_addr].plug_type = obj_arg[0];
        objects[obj_addr].location = obj_arg[1];
        objects[obj_addr].pricing_model = obj_arg[2];
        objects[obj_addr].num_charging_outlets = obj_arg[3];
        objects[obj_addr].charging_power = obj_arg[4];
        objects[obj_addr].fast_charging = obj_arg[5];
        emit NewObjectAdded(obj_addr, objects[obj_addr].location);
    }

    // Sets object to "deactivated" mode
    // Cannot reactivate once deleted
    function delete_object(
        /**OBJECT ID**/
        address obj_addr
    )
        /**MODIFIERS**/
        public
        admin_only()
        obj_not_deactivated(obj_addr)
    {
        objects[obj_addr].state = ObjectState.Deactivated;
    }

    // Sets object to "suspended" mode
    // Use reactivate_object function to reactivate object
    function suspend_object(
        /**OBJECT ID**/
        address obj_addr
    )
        /**MODIFIERS**/
        public
        admin_only()
        obj_not_deactivated(obj_addr)
    {
        objects[obj_addr].state = ObjectState.Suspended;
    }
    
    // Sets object to "active" mode
    // Cannot be used if object is "deactivated"
    function reactivate_object(
        /**OBJECT ID**/
        address obj_addr
    )
        /**MODIFIERS**/
        public
        admin_only()
        obj_not_deactivated(obj_addr)
    {
        objects[obj_addr].state = ObjectState.Active;
    }

    // Changes the attributes of a object
    // If attribute are blank "" skip to next attribute (no change done)
    // Note: Cannot set any attribute to empty string (blank)
    // Emits ObjectChanged event
    function change_attribs(
        /**OBJECT ID**/
        address obj_addr,
        /**OBJECT ATTRIBUTES**/
        string[6] memory obj_arg
    )
        /**MODIFIERS**/
        public
        admin_only()
        obj_active(obj_addr)
    {
        // CHANGE MAIN ATTRIBS
        // Check for empty field, if empty don't change
        bytes memory empty_test = bytes(obj_arg[0]);
        if (empty_test.length != 0) objects[obj_addr].plug_type = obj_arg[0];
        empty_test = bytes(obj_arg[1]);
        if (empty_test.length != 0) objects[obj_addr].location = obj_arg[1];
        empty_test = bytes(obj_arg[2]);
        if (empty_test.length != 0) objects[obj_addr].pricing_model = obj_arg[2];
        empty_test = bytes(obj_arg[3]);
        if (empty_test.length != 0) objects[obj_addr].num_charging_outlets = obj_arg[3];
        empty_test = bytes(obj_arg[4]);
        if (empty_test.length != 0) objects[obj_addr].charging_power = obj_arg[4];
        empty_test = bytes(obj_arg[5]);
        if (empty_test.length != 0) objects[obj_addr].fast_charging = obj_arg[5];

        // Emit event for successful object attribute change 
        emit ObjectChanged(obj_addr);
    }
}