
// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v4.6.0) (token/ERC20/IERC20.sol)

// File: @openzeppelin/contracts/token/ERC20/IERC20.sol


pragma solidity ^0.8.0;

/**
 * @dev Interface of the ERC20 standard as defined in the EIP.
 */
interface IERC20 {
    /**
     * @dev Emitted when `value` tokens are moved from one account (`from`) to
     * another (`to`).
     *
     * Note that `value` may be zero.
     */
    event Transfer(address indexed from, address indexed to, uint256 value);

    /**
     * @dev Emitted when the allowance of a `spender` for an `owner` is set by
     * a call to {approve}. `value` is the new allowance.
     */
    event Approval(address indexed owner, address indexed spender, uint256 value);

    /**
     * @dev Returns the amount of tokens in existence.
     */
    function totalSupply() external view returns (uint256);

    /**
     * @dev Returns the amount of tokens owned by `account`.
     */
    function balanceOf(address account) external view returns (uint256);

    /**
     * @dev Moves `amount` tokens from the caller's account to `to`.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transfer(address to, uint256 amount) external returns (bool);

    /**
     * @dev Returns the remaining number of tokens that `spender` will be
     * allowed to spend on behalf of `owner` through {transferFrom}. This is
     * zero by default.
     *
     * This value changes when {approve} or {transferFrom} are called.
     */
    function allowance(address owner, address spender) external view returns (uint256);

    /**
     * @dev Sets `amount` as the allowance of `spender` over the caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * IMPORTANT: Beware that changing an allowance with this method brings the risk
     * that someone may use both the old and the new allowance by unfortunate
     * transaction ordering. One possible solution to mitigate this race
     * condition is to first reduce the spender's allowance to 0 and set the
     * desired value afterwards:
     * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
     *
     * Emits an {Approval} event.
     */
    function approve(address spender, uint256 amount) external returns (bool);

    /**
     * @dev Moves `amount` tokens from `from` to `to` using the
     * allowance mechanism. `amount` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool);
}

// File: Remittance.sol


pragma solidity ^0.8.0;

contract Remittance {
    address public owner;
    IERC20 public cUSD;

    struct Transaction {
        uint256 amount;
        uint256 fee;
        bool isProcessed;
    }

    mapping(bytes32 => Transaction) public transactions;

    event TransferRequested(address indexed sender, bytes32 indexed transactionId, uint256 amount);
    event TransferProcessed(address indexed recipient, bytes32 indexed transactionId, uint256 amount);

    constructor(address _cUSDAddress) {
        owner = msg.sender;
        cUSD = IERC20(_cUSDAddress);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function.");
        _;
    }

    function requestTransfer(address _recipient, uint256 _amount, uint256 _fee) external {
        require(_amount > 0, "Amount must be greater than zero.");
        require(_fee >= 0, "Fee must be non-negative.");

        bytes32 transactionId = keccak256(abi.encodePacked(msg.sender, _recipient, _amount, _fee));
        require(!transactions[transactionId].isProcessed, "Transaction already processed.");

        transactions[transactionId] = Transaction(_amount, _fee, false);
        cUSD.transferFrom(msg.sender, address(this), _amount + _fee);

        emit TransferRequested(msg.sender, transactionId, _amount);
    }

    function processTransfer(address _recipient, bytes32 _transactionId) external onlyOwner {
        require(!transactions[_transactionId].isProcessed, "Transaction already processed.");

        Transaction storage transaction = transactions[_transactionId];
        cUSD.transfer(_recipient, transaction.amount);
        cUSD.transfer(owner, transaction.fee);

        transaction.isProcessed = true;

        emit TransferProcessed(_recipient, _transactionId, transaction.amount);
    }
}
