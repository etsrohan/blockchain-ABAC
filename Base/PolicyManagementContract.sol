// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract PolicyManagement {
    // ENUMS
    enum PolicyState {NotActive, Active, Suspended}

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
    // mode = 1 -> dynamic control ON (Check if within allowed time)
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
    event DuplicatePolicyExist(string[6] subject, string[6] object);
    event PolicyChanged(uint256 pol_id);
    event PolicyDeleted(uint256 pol_id);
    event PolicyNotExist(string[6] subject, string[6] object);

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }

    // VARIABLES
    address private admin;
    uint256 public total_policies;

    Policy[]  policies;
    uint256[] ret_list;

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
        total_policies = 0;
    }
    
    
    // Adds new policy with given subject, object, actions, context
    // Checks if policy already exists, if it doesn't then adds new policy
    // If policy already exists then emits DuplicatePolicyExist event
    function policy_add(
        /**SUBJECT ARGUMENTS**/
        string[6] memory sub_arg,
        /**OBJECT ARGUMENTS**/
        string[6] memory obj_arg,
        /**ACTION ARGUMENTS**/
        bool[3] memory act_arg,
        /**CONTEXT ARGUMENTS**/
        uint8 con_mode,
        uint256[2] memory con_time
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        if (find_exact_match_policy(sub_arg, obj_arg) == -1){
            // Generating pol_id for new policy
            uint256 pol_id = total_policies;
            total_policies++;
            // Pushing policy arguments into a new policy
            policies.push(Policy(
                PolicyState.Active,
                Subject(sub_arg[0], sub_arg[1], sub_arg[2], sub_arg[3], sub_arg[4], sub_arg[5]), 
                Object(obj_arg[0], obj_arg[1], obj_arg[2], obj_arg[3], obj_arg[4], obj_arg[5]), 
                Action(act_arg[0], act_arg[1], act_arg[2]), 
                Context(con_mode, con_time[0], con_time[1])));
    
            emit PolicyAdded(pol_id);
        } else {
            emit DuplicatePolicyExist(sub_arg, obj_arg);
        }
    }


    // Deletes an existing policy with given subject and object attributes
    // Finds exact match policy and then deletes the policy
    // If no policy found then emits PolicyNotExist event
    function policy_delete(
        /**SUBJECT ARGUMENTS**/
        string[6] memory sub_arg,
        /**OBJECT ARGUMENTS**/
        string[6] memory obj_arg
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        int pol_id = find_exact_match_policy(sub_arg, obj_arg);
        
        // check to see if policy exists
        // if it does then pop that policy out of policies
        // if not then emit event PolicyNotExist
        if (pol_id != -1){
            policies[uint256(pol_id)] = policies[policies.length - 1];
            policies.pop();
            total_policies--;
            emit PolicyDeleted(uint256(pol_id));
        } else {
            emit PolicyNotExist(sub_arg, obj_arg);
        }
    }


    // Suspends a given policy using pol_id
    // Use find_exact_match_policy function to find pol_id
    function policy_suspend(
        /**POLICY ID**/
        uint256 pol_id
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        policies[pol_id].state = PolicyState.Suspended;
    }

    // Reactivates an already suspended policy using pol_id
    // Use find_exact_match_policy function to find pol_id
    function policy_reactivate(
        /**POLICY ID**/
        uint256 pol_id
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        policies[pol_id].state = PolicyState.Active;
    }
    
    
    // Gives policy information using pol_id
    // To be used using find_match_policy function to iterate over
    function get_policy(
        /**POLICY ID**/
        uint256 pol_id
    )
        /**MODIFIERS**/
        view
        public
        returns (Policy memory)
    {
        return policies[pol_id];
    }
    

    // Updates already existing policy with new subject/object/action/context arguments
    // Only updates action and context fields and cannot update subject/object arguments
    // Note: To make a policy with empty fields for object and subject make new
    // policy using policy_add function
    // If policy doesn't exist then emits PolicyNotExist event
    function policy_update(
        /**SUBJECT ARGUMENTS**/
        string[6] memory sub_arg,
        /**OBJECT ARGUMENTS**/
        string[6] memory obj_arg,
        /**ACTION ARGUMENTS**/
        bool[3] memory act_arg,
        /**CONTEXT ARGUMENTS**/
        uint8 con_mode,
        uint256[2] memory con_arg
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        // Get pol_id from find_exact_match_policy fucntion
        int pol_id = find_exact_match_policy(sub_arg, obj_arg);
        
        if (pol_id != -1){
            require(policies[uint256(pol_id)].state == PolicyState.Active);
            
            // Change Actions Permitted
            policies[uint256(pol_id)].action.read = act_arg[0];
            policies[uint256(pol_id)].action.write = act_arg[1];
            policies[uint256(pol_id)].action.execute = act_arg[2];
            // Change Context
            policies[uint256(pol_id)].context.mode = con_mode;
            policies[uint256(pol_id)].context.start_time = con_arg[0];
            policies[uint256(pol_id)].context.end_time = con_arg[1];
            
            emit PolicyChanged(uint256(pol_id));
        } else {
            emit PolicyNotExist(sub_arg, obj_arg);
        }
    }


    // This Function checks every policy in the policies list/array and returns the first
    // element that EXACTLY MATCHES the given arguments
    // ELSE: it returns -1 if none were found
    function find_exact_match_policy (
        /**SUBJECT ARGUMENTS**/
        string[6] memory sub_arg,
        /**OBJECT ARGUMENTS**/
        string[6] memory obj_arg
    )
        /**MODIFIERS**/
        view
        public /**LATER CHANGE TO INTERNAL**/
        returns (int)
    {
        uint256 count;
        int ret = -1;
        for (count = 0; count < total_policies; count++){
            // Subject Comparison
            if (keccak256(abi.encodePacked(policies[count].subject.name))         != keccak256(abi.encodePacked(sub_arg[0]))) continue;
            if (keccak256(abi.encodePacked(policies[count].subject.organization)) != keccak256(abi.encodePacked(sub_arg[1]))) continue;
            if (keccak256(abi.encodePacked(policies[count].subject.department))   != keccak256(abi.encodePacked(sub_arg[2]))) continue;
            if (keccak256(abi.encodePacked(policies[count].subject.lab))          != keccak256(abi.encodePacked(sub_arg[3]))) continue;
            if (keccak256(abi.encodePacked(policies[count].subject.role))         != keccak256(abi.encodePacked(sub_arg[4]))) continue;
            if (keccak256(abi.encodePacked(policies[count].subject.other))        != keccak256(abi.encodePacked(sub_arg[5]))) continue;
            // Object Comparison
            if (keccak256(abi.encodePacked(policies[count].object.name))          != keccak256(abi.encodePacked(obj_arg[0]))) continue;
            if (keccak256(abi.encodePacked(policies[count].object.organization))  != keccak256(abi.encodePacked(obj_arg[1]))) continue;
            if (keccak256(abi.encodePacked(policies[count].object.department))    != keccak256(abi.encodePacked(obj_arg[2]))) continue;
            if (keccak256(abi.encodePacked(policies[count].object.lab))           != keccak256(abi.encodePacked(obj_arg[3]))) continue;
            if (keccak256(abi.encodePacked(policies[count].object.place))         != keccak256(abi.encodePacked(obj_arg[4]))) continue;
            if (keccak256(abi.encodePacked(policies[count].object.name))          != keccak256(abi.encodePacked(obj_arg[5]))) continue;
            // Set ret as count and end loop
            ret = int(count);
            break;
        }
        return ret;
    }
    
    
    // This Function checks every policy in the policies list/array and returns
    // every element that somewhat matches the arguments given
    // if the argument or policy field is "" empty string (Applies to All) then it checks next field
    // returns empty list if no matches were found.
    function find_match_policy(
        /**SUBJECT ARGUMENTS**/
        string[6] memory sub_arg,
        /**OBJECT ARGUMENTS**/
        string[6] memory obj_arg
    )
        /**MODIFIERS**/
        public
    {
        uint256 count;
        uint256 i;
        
        // empty the ret_list before adding new elements
        for (i = ret_list.length; i > 0; i--){
            ret_list.pop();
        }
        
        // check every field for similarity subject/object
        // if any field is empty on policy or sub/obj side then move to next field
        // if any field doesn't match then continue to next policy
        for (count = 0; count < total_policies; count++){
            // Subject Comparison
            if ((keccak256(abi.encodePacked(sub_arg[0])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.name)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.name)) != keccak256(abi.encodePacked(sub_arg[0])))) continue;

            if ((keccak256(abi.encodePacked(sub_arg[1])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.organization)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.organization)) != keccak256(abi.encodePacked(sub_arg[1])))) continue;

            if ((keccak256(abi.encodePacked(sub_arg[2])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.department)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.department)) != keccak256(abi.encodePacked(sub_arg[2])))) continue;

            if ((keccak256(abi.encodePacked(sub_arg[3])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.lab)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.lab)) != keccak256(abi.encodePacked(sub_arg[3])))) continue;

            if ((keccak256(abi.encodePacked(sub_arg[4])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.role)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.role)) != keccak256(abi.encodePacked(sub_arg[4])))) continue;

            if ((keccak256(abi.encodePacked(sub_arg[5])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.other)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].subject.other)) != keccak256(abi.encodePacked(sub_arg[5])))) continue;

            // Object Comparison
            if ((keccak256(abi.encodePacked(obj_arg[0])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.name)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.name)) != keccak256(abi.encodePacked(obj_arg[0])))) continue;

            if ((keccak256(abi.encodePacked(obj_arg[1])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.organization)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.organization)) != keccak256(abi.encodePacked(obj_arg[1])))) continue;

            if ((keccak256(abi.encodePacked(obj_arg[2])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.department)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.department)) != keccak256(abi.encodePacked(obj_arg[2])))) continue;

            if ((keccak256(abi.encodePacked(obj_arg[3])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.lab)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.lab)) != keccak256(abi.encodePacked(obj_arg[3])))) continue;
                
            if ((keccak256(abi.encodePacked(obj_arg[4])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.place)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.place)) != keccak256(abi.encodePacked(obj_arg[4])))) continue;

            if ((keccak256(abi.encodePacked(obj_arg[5])) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.other)) != keccak256(abi.encodePacked(""))) && 
                (keccak256(abi.encodePacked(policies[count].object.other)) != keccak256(abi.encodePacked(obj_arg[5])))) continue;

            // Add entry to list of similar policies
            ret_list.push(count);
        }
    }
    
    
    // Function to get the ret_list to see which policies are similar
    // to last query
    // Returns empty list if query resulted in no matches
    function get_ret_list (/**NO ARGS**/)
        /**MODIFIERS**/
        view
        public
        returns (uint256[] memory)
    {
        return ret_list;
    }


    // Function that takes ret_list (access_list), action, and time_stamp (add later)
    // and returns a boolean for access control
    // true: access granted, false: access denied
    function get_access (
        /**ARGUMENTS**/
        uint256[] memory access_list,
        uint8 action
    )
        external
        view
        returns (bool)
    {
        // Check to see if access list is empty
        if (access_list.length == 0){
            return false;
        }

        // Set read/write/execute to true if any policy in access_list allows to do so
        bool read = false;
        bool write = false;
        bool execute = false;
        for (uint256 i = 0; i < access_list.length; i++){
            if (policies[access_list[i]].context.mode == 0 || 
                (policies[access_list[i]].context.mode == 0 &&
                block.timestamp > policies[access_list[i]].context.start_time &&
                block.timestamp < policies[access_list[i]].context.end_time)){
                if (policies[access_list[i]].action.read){
                    read = true;
                }
                if (policies[access_list[i]].action.write){
                    write = true;
                }
                if (policies[access_list[i]].action.execute){
                    execute = true;
                }
            }
        }

        // Action: 0 = read, 1 = write, 2 = execute, 3 = read & write
        if (action == 0 && read) {
            return true;
        } else if (action == 1 && write) {
            return true;
        } else if (action == 2 && execute) {
            return true;
        } else if (action == 3 && read && write) {
            return true;
        } else {
            return false;
        }
    }
}