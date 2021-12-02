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

    // VARIABLES
    uint256 private total_supply;
    address private access_contract;
    address private admin;

    mapping (address => uint256) private balances;
    mapping (address => mapping (address => uint256)) private allowed;

    // EVENTS
    event Transfer(address indexed sender, address indexed receiver, uint256 num_tokens);
    event Approval(address indexed owner, address indexed delegate, uint256 num_tokens);

    // MODIFIERS
    modifier access_contract_only(){
        msg.sender == access_contract;
        _;
    }
    modifier admin_only(){
        msg.sender == admin;
        _;
    }

    // FUNCTIONS
    constructor(uint256 total)
    {
        total_supply = total;
        balances[msg.sender] = total_supply;
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
        returns (uint256)
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
        require (num_tokens <= balances[msg.sender]);
        balances[msg.sender] = SafeMath.sub(balances[msg.sender], num_tokens);
        balances[receiver] = SafeMath.add(balances[receiver], num_tokens);
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
        require (num_tokens <= balances[owner]);
        require (num_tokens <= allowed[owner][msg.sender]);
        balances[owner] = SafeMath.sub(balances[owner], num_tokens);
        allowed[owner][msg.sender] = SafeMath.sub(allowed[owner][msg.sender], num_tokens);
        balances[buyer] = SafeMath.add(balances[buyer], num_tokens);
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
        require (num_tokens <= balances[admin]);
        balances[admin] = SafeMath.sub(balances[admin], num_tokens);
        balances[buyer] = SafeMath.add(balances[buyer], num_tokens);
        emit Transfer(admin, buyer, num_tokens);
        return true;
    }

    // function to set the access control contract address into 
    // EVToken contract
    function set_access_address(
        address acc
    )
        admin_only()
        public
    {
        access_contract = acc;
    }
}