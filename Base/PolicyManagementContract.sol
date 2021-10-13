// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract PolicyManagement {
    // ENUMS
    enum PolicyState {NotActive, Active, Suspended, Deactivated}

    // STRUCTS
    // Object Attributes
    struct Object{
        string name;
        string organization;
        string department;
        string lab;
        string place;
        string other;
    }

    // Subject Attributes
    struct Subject{
        string name;
        string organization;
        string department;
        string lab;
        string role;
        string other;
    }

    // Actions allowed
    struct Action{
        bool read;
        bool write;
        bool execute;
    }

    // Context: Mode = dynamic access control i.e.
    // mode = 0 -> dynamic control OFF (don't check time)
    // mode = 1 -> dynamic control ON (Check if withing allowed time)
    struct Context{
        uint8 mode;
        uint256 start_time;
        uint256 end_time;
        // uint256 min_interval;
    }

    // Policy Structure
    // Contains sub/obj attribs, possible actions and context.
    struct Policy {
        PolicyState state;
        Subject subject;
        Object object;
        Action action;
        Context context;
    }

    // EVENTS
    event PolicyAdded(uint256 pol_id);
    event PolicyChanged(uint256 pol_id);

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }
    modifier policy_active(uint256 pol_id){
        require(policies[pol_id].state == PolicyState.Active);
        _;
    }
    modifier policy_not_deactivated(uint256 pol_id){
        require(policies[pol_id].state != PolicyState.Deactivated);
        _;
    }

    // VARIABLES
    address admin;
    uint256 public total_policies;

    mapping (uint => Policy) public policies;

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
    }
    
    function policy_add(
        /**SUBJECT ARGUMENTS**/
        string[] memory sub_arg,
        /**OBJECT ARGUMENTS**/
        string[] memory obj_arg,
        /**ACTION ARGUMENTS**/
        bool[] memory act_arg,
        /**CONTEXT ARGUMENTS**/
        uint8 con_mode,
        uint256[] memory con_time
    )
        public
        admin_only()
    {
        // Generating pol_id for new policy
        uint256 pol_id = total_policies;
        total_policies++;
        // Setting policy state to "Active"
        policies[pol_id].state = PolicyState.Active;
        // Add Subject Info
        policies[pol_id].subject.name = sub_arg[0];
        policies[pol_id].subject.organization = sub_arg[1];
        policies[pol_id].subject.department = sub_arg[2];
        policies[pol_id].subject.lab = sub_arg[3];
        policies[pol_id].subject.role = sub_arg[4];
        policies[pol_id].subject.other = sub_arg[5];
        // Add Object Info
        policies[pol_id].object.name = obj_arg[0];
        policies[pol_id].object.organization = obj_arg[1];
        policies[pol_id].object.department = obj_arg[2];
        policies[pol_id].object.lab = obj_arg[3];
        policies[pol_id].object.place = obj_arg[4];
        policies[pol_id].object.other = obj_arg[5];
        // Add Actions Permitted
        policies[pol_id].action.read = act_arg[0];
        policies[pol_id].action.write = act_arg[1];
        policies[pol_id].action.execute = act_arg[2];
        // Add Context
        policies[pol_id].context.mode = con_mode;
        policies[pol_id].context.start_time = con_time[0];
        policies[pol_id].context.end_time = con_time[1];

        emit PolicyAdded(pol_id);
    }

    function policy_delete(
        uint256 pol_id
    )
        public
        admin_only()
        policy_not_deactivated(pol_id)
    {
        policies[pol_id].state = PolicyState.Deactivated;
    }

    function policy_suspend(
        uint256 pol_id
    )
        public
        admin_only()
        policy_not_deactivated(pol_id)
    {
        policies[pol_id].state = PolicyState.Suspended;
    }

    function policy_reactivate(
        uint256 pol_id
    )
        public
        admin_only()
        policy_not_deactivated(pol_id)
    {
        policies[pol_id].state = PolicyState.Active;
    }


    function policy_update(
        /**POLICY ID**/
        uint256 pol_id,
        /**SUBJECT ARGUMENTS**/
        string[] memory sub_arg,
        /**SUBJECT ARGUMENTS**/
        string[] memory obj_arg,
        /**SUBJECT ARGUMENTS**/
        bool[] memory act_arg,
        /**SUBJECT ARGUMENTS**/
        uint8 con_mode,
        uint256[] memory con_arg

    )
        public
        admin_only()
        policy_active(pol_id)
    {
        // Change Subject Info (if string not empty)
        bytes memory empty_test = bytes(sub_arg[0]);
        if (empty_test.length != 0) policies[pol_id].subject.name = sub_arg[0];
        empty_test = bytes(sub_arg[1]);
        if (empty_test.length != 0) policies[pol_id].subject.organization = sub_arg[1];
        empty_test = bytes(sub_arg[2]);
        if (empty_test.length != 0) policies[pol_id].subject.department = sub_arg[2];
        empty_test = bytes(sub_arg[3]);
        if (empty_test.length != 0) policies[pol_id].subject.lab = sub_arg[3];
        empty_test = bytes(sub_arg[4]);
        if (empty_test.length != 0) policies[pol_id].subject.role = sub_arg[4];
        empty_test = bytes(sub_arg[5]);
        if (empty_test.length != 0) policies[pol_id].subject.other = sub_arg[5];
        // Change Object Info (if string not empty)
        empty_test = bytes(obj_arg[0]);
        if (empty_test.length != 0) policies[pol_id].object.name = obj_arg[0];
        empty_test = bytes(obj_arg[1]);
        if (empty_test.length != 0) policies[pol_id].object.organization = obj_arg[1];
        empty_test = bytes(obj_arg[2]);
        if (empty_test.length != 0) policies[pol_id].object.department = obj_arg[2];
        empty_test = bytes(obj_arg[3]);
        if (empty_test.length != 0) policies[pol_id].object.lab = obj_arg[3];
        empty_test = bytes(obj_arg[4]);
        if (empty_test.length != 0) policies[pol_id].object.place = obj_arg[4];
        empty_test = bytes(obj_arg[5]);
        if (empty_test.length != 0) policies[pol_id].object.other = obj_arg[5];
        // Change Actions Permitted
        policies[pol_id].action.read = act_arg[0];
        policies[pol_id].action.write = act_arg[1];
        policies[pol_id].action.execute = act_arg[2];
        // Change Context
        policies[pol_id].context.mode = con_mode;
        policies[pol_id].context.start_time = con_arg[0];
        policies[pol_id].context.end_time = con_arg[1];
        
        emit PolicyChanged(pol_id);
    }
    
    // function get_bytes(string memory word) pure public returns (bytes memory){
    //     return bytes(word);
    // }

    // function find_exact_match_policy()
    // function find_match_policy()
}