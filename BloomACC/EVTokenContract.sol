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
    // VARIABLES
    uint256 total_supply;
    address access_contract;
    address admin;

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

    function get_total_supply()
        public
        view
        returns (uint256)
    {
        return total_supply;
    }

    function get_balance(
        address token_owner
    )
        public
        view
        returns (uint256)
    {
        return balances[token_owner];
    }

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

    function set_access_address(
        address acc
    )
        admin_only()
        public
    {
        access_contract = acc;
    }
}