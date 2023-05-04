import os
from web3 import Web3
from web3.middleware import geth_poa_middleware

import deploy


# Set up web3 connection
provider_url = os.environ.get("CELO_PROVIDER_URL")
w3 = Web3(Web3.HTTPProvider(provider_url))
assert w3.is_connected(), "Not connected to a Celo node"

# Add PoA middleware to web3.py instance
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


abi = deploy.abi
contract_address = deploy.contract_address
private_key = deploy.private_key
deployer = deploy.deployer


contract = w3.eth.contract(address=contract_address, abi=abi)


def request_transfer(recipient, amount, fee):
    transaction_id = w3.solidity_keccak(
        ['address', 'address', 'uint256', 'uint256'], [deployer, recipient, amount, fee])
    transaction_id_hex = transaction_id.hex()

    nonce = w3.eth.get_transaction_count(deployer)
    txn = contract.functions.requestTransfer(recipient, amount, fee).build_transaction({
        'from': deployer,
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    return transaction_id_hex, txn_receipt


def process_transfer(recipient, transaction_id_hex):

    owner = recipient

    nonce = w3.eth.get_transaction_count(owner)
    gas_estimate = contract.functions.processTransfer(
        recipient, transaction_id_hex).estimate_gas({"from": owner})

    txn = contract.functions.processTransfer(recipient, transaction_id_hex).build_transaction({
        'from': owner,
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })

    owner_private_key = private_key
    signed_txn = w3.eth.account.sign_transaction(txn, owner_private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    return txn_receipt


if __name__ == "__main__":
    # Test the request_transfer function
    # Replace with the actual recipient address
    recipient = deployer
    amount = 1000  # Replace with the desired amount
    fee = 10  # Replace with the desired fee

    transaction_id_hex, txn_receipt = request_transfer(recipient, amount, fee)
    print(f"Transfer requested. Transaction ID: {transaction_id_hex}")
    print(f"Transaction receipt: {txn_receipt}")

    # Test the process_transfer function
    process_receipt = process_transfer(recipient, transaction_id_hex)
    print(f"Transfer processed. Transaction receipt: {process_receipt}")

