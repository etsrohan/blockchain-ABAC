// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract PolicyManagement {
    // ENUMS
    enum PolicyState {NotActive, Active, Suspended, Deactivated}

    // STRUCTS
    // Object Attributes
    struct Object{
        bytes32 name;
        bytes32 organization;
        bytes32 department;
        bytes32 lab;
        bytes32 place;
        bytes32 other;
    }

    // Subject Attributes
    struct Subject{
        bytes32 name;
        bytes32 organization;
        bytes32 department;
        bytes32 lab;
        bytes32 role;
        bytes32 other;
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
        /*ADD ARGUMENTS LATER*/
    )
        public
        admin_only()
    {
        uint256 pol_id = total_policies;
        total_policies++;
        policies[pol_id].state = PolicyState.Active;
        // Add Subject and Object Info
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

    // function find_exact_match_policy()
    // function find_match_policy()
}