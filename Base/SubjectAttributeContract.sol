// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract SubjectAttribute {
    // ENUMS
    enum SubjectState {NotCreated, Active, Deactivated}

    // STRUCTS
    struct Subject{
        SubjectState state;
        bytes32 name;
        bytes32 organization;
        bytes32 department;
        bytes32 lab;
        bytes32 role;
        bytes32 other;
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

    // EVENTS
    event NewSubjectAdded(uint256 sub_id);

    // FUNCTIONS
    function subject_add(
        bytes32 sub_name
        /*ADD ARGUMENTS*/
    )
        public
        admin_only()
    {
        uint256 sub_id = num_subjects;
        num_subjects++;
        subjects[sub_id].state = SubjectState.Active;
        // ADD OTHER ATTRIBS
        subjects[sub_id].name = sub_name;
    }

    function delete_subject(
        uint256 sub_id
    )
        public
        admin_only()
    {
        subjects[sub_id].state = SubjectState.Deactivated;
    }

    // function change_attribs(uint256 sub_id)
}