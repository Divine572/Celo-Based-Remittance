import json
import os
from solcx import compile_standard, install_solc
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
from web3 import Web3


load_dotenv()


# Install specific Solidity compiler version
install_solc("0.8.0")


# Set up web3 connection
provider_url = os.environ.get("CELO_PROVIDER_URL")
w3 = Web3(Web3.HTTPProvider(provider_url))
assert w3.is_connected(), "Not connected to a Celo node"

# Set deployer account and private key
deployer = os.environ.get("CELO_DEPLOYER_ADDRESS")
private_key = os.environ.get("CELO_DEPLOYER_PRIVATE_KEY")

with open("FlattenedRemittance.sol", "r") as file:
    solidity_code = file.read()


# Add Geth POA middleware to handle extraData field in Celo transactions
w3.middleware_onion.inject(geth_poa_middleware, layer=0)



# Compile the Solidity smart contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "FlattenedRemittance.sol": {
            "content": solidity_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["metadata", "evm.bytecode", "evm.deployedBytecode", "abi"]
            }
        },
        "optimizer": {
            "enabled": True,
            "runs": 200
        }
    }
})


# Get the bytecode, contract data, and ABI
contract_data = compiled_sol['contracts']['FlattenedRemittance.sol']['Remittance']
bytecode = contract_data['evm']['bytecode']['object']
abi = json.loads(contract_data['metadata'])['output']['abi']


# Deploy the contract
nonce = w3.eth.get_transaction_count(deployer)
transaction = {
    'nonce': nonce,
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'data': bytecode,
}
signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

# Get the contract address
contract_address = transaction_receipt['contractAddress']
print(f"Contract deployed at address: {contract_address}")
