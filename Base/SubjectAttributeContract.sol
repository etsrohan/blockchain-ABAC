// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract SubjectAttribute {
    // ENUMS
    enum SubjectState {NotCreated, Active, Deactivated}

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

    // EVENTS
    event NewSubjectAdded(uint256 sub_id);

    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
    }
    
    function subject_add(
        string memory sub_name
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