// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract AccessControl {

    address admin;
    // FUNCTIONS
    constructor()
    {
        admin = msg.sender;
    }
    
    function access_control(
        int256 sub_id,
        int256 obj_id
        /**ADD ARGUMENTS**/
    )
        public
        /**ADD MODIFIERS**/
    {
        
    }
}