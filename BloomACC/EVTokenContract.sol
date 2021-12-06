// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

library SafeMath { // Only relevant functions
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        assert(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal pure returns (uint256)   {
        uint256 c = a + b;
        assert(c >= a);
        return c;
    }
}

contract EVToken {
    using SafeMath for uint256;

    // STRUCTS
    struct account{
        uint256 balance;
        uint256 expiration_time;
    }

    // VARIABLES
    uint256 private total_supply;
    address private access_contract;
    address private admin;

    mapping (address => account) private balances;
    mapping (address => mapping (address => uint256)) private allowed;

    // EVENTS
    event Transfer(address indexed sender, address indexed receiver, uint256 num_tokens);
    event Approval(address indexed owner, address indexed delegate, uint256 num_tokens);
    event AdminTransfer(address indexed admin, address indexed receiver, uint256 num_tokens, uint256 expiration_time);
    event TokenRedeemed(address indexed subject, uint256 num_tokens, uint256 redeem_time);
    event TokenRefunded(address indexed admin, address indexed subject, uint256 num_tokens, uint256 refund_time);
    event TimeExtended(address indexed subject, uint256 new_time);

    // MODIFIERS
    modifier access_contract_only(){
        require (msg.sender == access_contract);
        _;
    }
    modifier admin_only(){
        require (msg.sender == admin);
        _;
    }

    // FUNCTIONS
    constructor(uint256 total)
    {
        total_supply = total;
        balances[msg.sender].balance = total_supply;
        balances[msg.sender].expiration_time = 0;
        admin = msg.sender;
    }

    // returns total supply of EVToken
    function get_total_supply()
        public
        view
        returns (uint256)
    {
        return total_supply;
    }

    // returns token balance of a specific address
    function get_balance(
        address token_owner
    )
        public
        view
        returns (account memory)
    {
        return balances[token_owner];
    }

    // function to transfer tokens from self to receiver
    function transfer(
        address receiver,
        uint256 num_tokens
    )
        public
        returns (bool)
    {
        require (num_tokens <= balances[msg.sender].balance);
        balances[msg.sender].balance = SafeMath.sub(balances[msg.sender].balance, num_tokens);
        balances[receiver].balance = SafeMath.add(balances[receiver].balance, num_tokens);
        emit Transfer(msg.sender, receiver, num_tokens);
        return true;
    }

    // appoint a third party to delegate a transaction with num_tokens
    function approve(
        address delegate,
        uint256 num_tokens
    )
        public
        returns (bool)
    {
        allowed[msg.sender][delegate] = num_tokens;
        emit Approval(msg.sender, delegate, num_tokens);
        return true;
    }

    // check allowance that delegate can transfer from owner for transaction
    function allowance(
        address owner,
        address delegate
    )
        public
        view
        returns (uint256)
    {
        return allowed[owner][delegate];
    }

    // to be used by the delegate to transfer tokens from owner to a buyer
    function transfer_from(
        address owner,
        address buyer,
        uint256 num_tokens
    )
        public
        returns (bool)
    {
        require (num_tokens <= balances[owner].balance);
        require (num_tokens <= allowed[owner][msg.sender]);
        balances[owner].balance = SafeMath.sub(balances[owner].balance, num_tokens);
        allowed[owner][msg.sender] = SafeMath.sub(allowed[owner][msg.sender], num_tokens);
        balances[buyer].balance = SafeMath.add(balances[buyer].balance, num_tokens);
        emit Transfer(owner, buyer, num_tokens);
        return true;
    }

    // To be used by the access control contract to transfer funds from admin
    // to the caller of access request if access is granted
    function transfer_from_admin(
        address buyer,
        uint256 num_tokens
    )
        external
        access_contract_only()
        returns (bool)
    {
        require (num_tokens <= balances[admin].balance);
        balances[admin].balance = SafeMath.sub(balances[admin].balance, num_tokens);
        balances[buyer].balance = SafeMath.add(balances[buyer].balance, num_tokens);
        balances[buyer].expiration_time = block.timestamp + 300;
        // Emit an event to indicate token being released for successful access
        // and has a 5 minute expiration time
        emit AdminTransfer(admin, buyer, num_tokens, balances[buyer].expiration_time);
        return true;
    }

    // Function to redeem token given for successful access
    // Emits TokenRedeemed event to send success message
    function redeem_token(
        uint256 num_tokens
    )
        public
        returns(bool)
    {
        require (balances[msg.sender].balance >= 1);
        require (balances[msg.sender].expiration_time >= block.timestamp);
        balances[admin].balance = SafeMath.add(balances[admin].balance, num_tokens);
        balances[msg.sender].balance = SafeMath.sub(balances[msg.sender].balance, num_tokens);
        // Emit TokenRedeemed event to let the system know that token was redeemed
        emit TokenRedeemed(msg.sender, num_tokens, block.timestamp);
        return true;
    }


    // Refund a token back to admin after expiration time has passed.
    // Emits TokenRefunded event so payment refund can also start being processed 
    function refund_token(
        address subject,
        uint256 num_tokens
    )
        public
        admin_only()
        returns(bool)
    {
        require (balances[subject].balance >= 1);
        require (balances[subject].expiration_time <= block.timestamp);
        balances[admin].balance = SafeMath.add(balances[admin].balance, num_tokens);
        balances[subject].balance = SafeMath.sub(balances[subject].balance, num_tokens);
        // Emit TokenRefunded event to let subject know that token was refunded
        // for token expiration
        emit TokenRefunded(admin, subject, num_tokens, block.timestamp);
        return true;
    }

    // A function to extend the expiration time for a token given to a subject
    // emits TimeExtended event for a subject
    function extend_expiration(
        address subject,
        uint256 time_extension
    )
        public
        admin_only()
        returns (bool)
    {
        balances[subject].expiration_time = SafeMath.add(block.timestamp, time_extension);
        // Emit TimeExtended event
        emit TimeExtended(subject, balances[subject].expiration_time);
        return true;
    }

    // Function to set the access control contract address into 
    // EVToken contract so that the access control contract can 
    // send direct transactions from admin account and receiver
    function set_access_address(
        address acc
    )
        admin_only()
        public
    {
        access_contract = acc;
    }
}