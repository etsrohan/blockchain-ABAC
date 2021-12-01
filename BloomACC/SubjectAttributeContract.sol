// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract SubjectAttribute {
    // ENUMS
    enum SubjectState {NotCreated, Active, Suspended, Deactivated}

    // STRUCTS
    struct Subject{
        SubjectState state;
        string manufacturer;
        string current_location;
        string vehicle_type;
        string charging_efficiency;
        string discharging_efficiency;
        string energy_capacity;
        uint256 ToMFR;
    }

    struct BloomFilter{
        uint256 bitmap;
        uint8 hash_count;
    }

    // VARIABLES
    address admin;
    uint256 num_subjects;
    BloomFilter filter;

    mapping (uint256 => Subject) public subjects;

    // MODIFIERS
    modifier admin_only(){
        require(msg.sender == admin);
        _;
    }
    modifier sub_active(uint256 sub_id){
        require(subjects[sub_id].state == SubjectState.Active);
        _;
    }
    modifier sub_not_deactivated(uint256 sub_id){
        require(subjects[sub_id].state != SubjectState.Deactivated);
        _;
    }

    // EVENTS
    event NewSubjectAdded(uint256 sub_id, string manufacturer);
    event SubjectChanged(uint256 sub_id);

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
        num_subjects = 0;
        filter.bitmap = 0;
        filter.hash_count = 5;
    }
    
    // Adds a new subject with given attributes:
    // manufacturer, current_location, vehicle_type, charging_efficiency, discharging_efficiency, energy_capacity, ToMFR
    // Emits NewSubjectAdded event with the sub_id
    function subject_add(
        /**SUBJECT ATTRIBUTES**/
        string[6] memory sub_arg
    )
        /**MODIFIERS**/
        public
        admin_only()
    {
        uint256 sub_id = num_subjects;
        num_subjects++;
        subjects[sub_id].state = SubjectState.Active;
        // ADD MAIN ATTRIBS
        subjects[sub_id].manufacturer = sub_arg[0];
        subjects[sub_id].current_location = sub_arg[1];
        subjects[sub_id].vehicle_type = sub_arg[2];
        subjects[sub_id].charging_efficiency = sub_arg[3];
        subjects[sub_id].discharging_efficiency = sub_arg[4];
        subjects[sub_id].energy_capacity = sub_arg[5];
        subjects[sub_id].ToMFR = 0;
        // ADD SUBJECT TO BLOOMFILTER
        add_bitmap(sub_id);
        // Emit event for new subject
        emit NewSubjectAdded(sub_id, subjects[sub_id].manufacturer);
    }

    // Adds a subject to bloom filter
    // By default hash_count is 5 in constructor
    // hash_count is number of times the sub_id gets hashed
    function add_bitmap(
        /**SUBJECT ID**/
        uint256 sub_id
    )
        /**MODIFIERS**/
        internal
    {
        require(filter.hash_count > 0, "Hash count cannot be zero!");
        for(uint i = 0; i < filter.hash_count; i++) {
            uint256 index = uint256(keccak256(abi.encodePacked(sub_id, i))) % 256;
            require(index < 256, "Overflow Error!");
            uint256 bit_place = 1 << index;
            filter.bitmap = filter.bitmap | bit_place;
        }
    }

    // Sets subject to "deactivated" mode
    // Cannot reactivate once deleted
    function delete_subject(
        /**SUBJECT ID**/
        uint256 sub_id
    )
        /**MODIFIERS**/
        public
        admin_only()
        sub_not_deactivated(sub_id)
    {
        subjects[sub_id].state = SubjectState.Deactivated;
    }

    // Sets subject to "suspended" mode
    // Use reactivate_subject function to reactivate subject
    function suspend_subject(
        /**SUBJECT ID**/
        uint256 sub_id
    )
        /**MODIFIERS**/
        public
        admin_only()
        sub_not_deactivated(sub_id)
    {
        subjects[sub_id].state = SubjectState.Suspended;
    }
    
    // Sets subject to "active" mode
    // Cannot be used if subject is "deactivated"
    function reactivate_subject(
        /**SUBJECT ID**/
        uint256 sub_id
    )
        /**MODIFIERS**/
        public
        admin_only()
        sub_not_deactivated(sub_id)
    {
        subjects[sub_id].state = SubjectState.Active;
    }

    // Check the sub_id with the existing bloom filter
    // to see if sub_id exists.
    // Returns true if sub_id may exist
    // Returns false if sub_id definitely doesn't exist
    function check_bitmap(
        /**SUBJECT ID**/
        uint256 sub_id
    )
        /**MODIFIERS**/
        external
        view
        returns(bool)
    {
        require(filter.hash_count > 0, "Hash count cannot be zero");
        for(uint256 i = 0; i < filter.hash_count; i++){
            uint256 index = uint256(keccak256(abi.encodePacked(sub_id, i))) % 256;
            require(index < 256, "Overflow Error!");
            uint256 bit_place = 1 << index;
            if((filter.bitmap & bit_place) == 0) return false;
        }
        return true;
    }

    // Changes the attributes of a subject
    // If attribute are blank "" skip to next attribute (no change done)
    // Note: Cannot set any attribute to empty string (blank)
    // Emits SubjectChanged event
    function change_attribs(
        /**SUBJECT ID**/
        uint256 sub_id,
        /**SUBJECT ATTRIBUTES**/
        string[6] memory sub_arg
    )
        /**MODIFIERS**/
        public
        admin_only()
        sub_active(sub_id)
    {
        // CHANGE MAIN ATTRIBS
        bytes memory empty_test = bytes(sub_arg[0]);
        if (empty_test.length != 0) subjects[sub_id].manufacturer = sub_arg[0];
        empty_test = bytes(sub_arg[1]);
        if (empty_test.length != 0) subjects[sub_id].current_location = sub_arg[1];
        empty_test = bytes(sub_arg[2]);
        if (empty_test.length != 0) subjects[sub_id].vehicle_type = sub_arg[2];
        empty_test = bytes(sub_arg[3]);
        if (empty_test.length != 0) subjects[sub_id].charging_efficiency = sub_arg[3];
        empty_test = bytes(sub_arg[4]);
        if (empty_test.length != 0) subjects[sub_id].discharging_efficiency = sub_arg[4];
        empty_test = bytes(sub_arg[5]);
        if (empty_test.length != 0) subjects[sub_id].energy_capacity = sub_arg[5];
        emit SubjectChanged(sub_id);
    }

    // Updates the Time of Most Frequent Request to
    // current time. To be used by the AccessControlContract.
    function update_tomfr(
        /**SUBJECT ID**/
        uint256 sub_id
    )
        external
        sub_active(sub_id)
    {
        subjects[sub_id].ToMFR = block.timestamp;
    }
}