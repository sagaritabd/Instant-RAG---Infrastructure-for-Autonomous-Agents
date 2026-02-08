from web3 import Web3
from payments.config import POLYGON_RPC, TREASURY_ADDRESS, USDC
from payments.ledger import credit

w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

def decode_agent(tx):
    data = tx.input or ""
    return data[-8:] if len(data) >= 8 else "anonymous"

def scan_block(block):
    b = w3.eth.get_block(block, full_transactions=True)

    for tx in b.transactions:
        if not tx.to:
            continue

        if tx.to.lower() == USDC.lower():
            receipt = w3.eth.get_transaction_receipt(tx.hash)

            for log in receipt.logs:
                if log.address.lower() == USDC.lower():
                    to = "0x" + log.topics[2].hex()[-40:]

                    if to.lower() == TREASURY_ADDRESS.lower():
                        amount = int(log.data, 16) / 1e6
                        agent = decode_agent(tx)
                        credit(agent, amount, tx.hash.hex())
