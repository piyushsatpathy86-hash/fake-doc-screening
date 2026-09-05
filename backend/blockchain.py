"""
blockchain.py
A minimal blockchain used to store a tamper-proof audit trail of
every document screening result. Each record's data is hashed
together with the previous block's hash, so any edit to old data
breaks the chain and can be detected by verify_chain().
"""

import hashlib
import json
from datetime import datetime


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """SHA256 hash of the block's contents."""
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, str(datetime.now()), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        """Add a new block with `data` (e.g. a screening record) and return it."""
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=str(datetime.now()),
            data=data,
            previous_hash=previous_block.hash,
        )
        self.chain.append(new_block)
        return new_block

    def verify_chain(self):
        """Return True if the chain has not been tampered with."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False

        return True

    def to_list(self):
        return [block.to_dict() for block in self.chain]


# Shared blockchain instance used across the whole app
blockchain = Blockchain()


if __name__ == "__main__":
    blockchain.add_block({"passport_number": "A1234567", "risk_score": 45})
    blockchain.add_block({"passport_number": "B7654321", "risk_score": 80})
    for block in blockchain.chain:
        print(block.to_dict())
    print("Chain valid?", blockchain.verify_chain())