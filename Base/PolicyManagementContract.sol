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

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }
    modifier policy_active(uint256 pol_id){
        require(policies[pol_id].state == PolicyState.Active);
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
    {
        policies[pol_id].state = PolicyState.Deactivated;
    }

    function policy_update(
        uint256 pol_id,
        uint256 stime,
        uint256 etime,
        bool suspend
        /*ADD MORE ARGS*/
    )
        public
        admin_only()
        policy_active(pol_id)
    {
        policies[pol_id].context.start_time = stime;
        policies[pol_id].context.end_time = etime;
        
        if (suspend) policies[pol_id].state == PolicyState.Suspended;
    }
    
    // function get_bytes(string memory word) pure public returns (bytes memory){
    //     return bytes(word);
    // }

    // function find_exact_match_policy()
    // function find_match_policy()
}