// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract SubjectAttribute {
    // ENUMS
    enum SubjectState {NotCreated, Active, Suspended, Deactivated}

    // STRUCTS
    struct Subject{
        SubjectState state;
        string name;
        string organization;
        string department;
        string lab;
        string role;
        string other;
    }

    // VARIABLES
    address admin;
    uint256 num_subjects;

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
    event NewSubjectAdded(uint256 sub_id);
    event SubjectChanged(uint256 sub_id);

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
    }
    
    function subject_add(
        /**ARGUMENTS LIST**/
        string[] memory sub_arg
    )
        public
        admin_only()
    {
        uint256 sub_id = num_subjects;
        num_subjects++;
        subjects[sub_id].state = SubjectState.Active;
        // ADD MAIN ATTRIBS
        subjects[sub_id].name = sub_arg[0];
        subjects[sub_id].organization = sub_arg[1];
        subjects[sub_id].department = sub_arg[2];
        subjects[sub_id].lab = sub_arg[3];
        subjects[sub_id].role = sub_arg[4];
        subjects[sub_id].other = sub_arg[5];
        emit NewSubjectAdded(sub_id);
    }

    function delete_subject(
        uint256 sub_id
    )
        public
        admin_only()
        sub_not_deactivated(sub_id)
    {
        subjects[sub_id].state = SubjectState.Deactivated;
    }

    function suspend_subject(
        uint256 sub_id
    )
        public
        admin_only()
        sub_not_deactivated(sub_id)
    {
        subjects[sub_id].state = SubjectState.Suspended;
    }

    function change_attribs(
        uint256 sub_id,
        string[] memory sub_arg
    )
        public
        admin_only()
        sub_active(sub_id)
    {
        // CHANGE MAIN ATTRIBS
        bytes memory empty_test = bytes(sub_arg[0]);
        if (empty_test.length != 0) subjects[sub_id].name = sub_arg[0];
        empty_test = bytes(sub_arg[1]);
        if (empty_test.length != 0) subjects[sub_id].organization = sub_arg[1];
        empty_test = bytes(sub_arg[2]);
        if (empty_test.length != 0) subjects[sub_id].department = sub_arg[2];
        empty_test = bytes(sub_arg[3]);
        if (empty_test.length != 0) subjects[sub_id].lab = sub_arg[3];
        empty_test = bytes(sub_arg[4]);
        if (empty_test.length != 0) subjects[sub_id].role = sub_arg[4];
        empty_test = bytes(sub_arg[5]);
        if (empty_test.length != 0) subjects[sub_id].other = sub_arg[5];
        emit SubjectChanged(sub_id);
    }
}