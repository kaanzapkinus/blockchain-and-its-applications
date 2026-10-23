"""
Miniature Blockchain Implementation for Lab 1
Course: Blockchain and its Application (Zima 2026/2027)
Instructor: Vishnu Suresh
Author: Kaan Yazıcıoğlu
"""

import hashlib
import json
import re
import time
from copy import deepcopy
from typing import Any, Dict, List, Tuple


def sha256_text(text: str) -> str:
    """Calculates the SHA-256 hexadecimal hash for an arbitrary text string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def calculate_block_hash(block: Dict[str, Any]) -> str:
    """Calculates deterministic SHA-256 hash for a block dictionary, excluding the 'hash' key."""
    data = {key: value for key, value in block.items() if key != "hash"}
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)


def make_block(
    index: int,
    transactions: List[str],
    previous_hash: str,
    timestamp: str,
    nonce: int = 0,
) -> Dict[str, Any]:
    """Constructs a new block and calculates its cryptographic hash."""
    block: Dict[str, Any] = {
        "index": index,
        "timestamp": timestamp,
        "transactions": transactions,
        "previous_hash": previous_hash,
        "nonce": nonce,
    }
    block["hash"] = calculate_block_hash(block)
    return block


def show_chain(blocks: List[Dict[str, Any]]) -> None:
    """Displays a summary of each block in the chain."""
    for block in blocks:
        print(
            "Block", block["index"],
            "hash", block["hash"][:12],
            "previous", block["previous_hash"][:12],
            "nonce", block["nonce"],
        )


def validate_chain(blocks: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Standard Part 3 validator checking block hash consistency and previous_hash links."""
    for position, block in enumerate(blocks):
        recalculated = calculate_block_hash(block)
        if block["hash"] != recalculated:
            return False, f"Block {position} has changed contents"
        if position > 0:
            expected_previous = blocks[position - 1]["hash"]
            if block["previous_hash"] != expected_previous:
                return False, f"Block {position} has a broken previous-hash link"
    return True, "Chain is valid"


def mine_block(
    index: int,
    transactions: List[str],
    previous_hash: str,
    timestamp: str,
    difficulty: int = 3,
) -> Tuple[Dict[str, Any], int]:
    """Mines a block using Proof of Work until its hash starts with the required number of zeros."""
    block: Dict[str, Any] = {
        "index": index,
        "timestamp": timestamp,
        "transactions": transactions,
        "previous_hash": previous_hash,
        "nonce": 0,
    }
    target = "0" * difficulty
    attempts = 0
    while True:
        attempts += 1
        digest = calculate_block_hash(block)
        if digest.startswith(target):
            block["hash"] = digest
            return block, attempts
        block["nonce"] += 1


# =====================================================================
# Enhanced Extensions for Tasks 1 & 2
# =====================================================================

TX_REGEX = re.compile(r"^(\S+)\s+pays\s+(\S+)\s+(.+)$")


def validate_transaction(tx: str) -> Tuple[bool, str]:
    """
    Validates a single transaction string based on Lab 1 Task 1 requirements:
    1. Must match format: '<Sender> pays <Receiver> <Amount>'
    2. Amount must be a positive numerical value (> 0).
    3. Sender and Receiver must be different entities.
    """
    if not isinstance(tx, str):
        return False, "Transaction is not a string"

    match = TX_REGEX.match(tx.strip())
    if not match:
        return False, f"Invalid transaction format (expected 'Sender pays Receiver Amount'): '{tx}'"

    sender, receiver, amount_str = match.groups()

    if sender == receiver:
        return False, f"Self-transfer detected: sender '{sender}' cannot be receiver"

    try:
        amount = float(amount_str)
    except ValueError:
        return False, f"Amount '{amount_str}' is not a valid number"

    if amount <= 0:
        return False, f"Amount must be strictly positive (> 0), got: {amount}"

    return True, f"Valid transaction ({sender} -> {receiver}: {amount})"


def validate_chain_enhanced(
    blocks: List[Dict[str, Any]],
    check_transactions: bool = True,
    difficulty: int = 0,
) -> Tuple[bool, str]:
    """
    Two-Layer Chain Validator:
    Layer 1 (Block Integrity):
      - Block hash matches recalculated contents
      - Previous-hash matches previous block's hash
      - (Optional) Hash satisfies PoW difficulty target

    Layer 2 (Transaction Validity):
      - Every transaction in every non-genesis block adheres to semantic rules
    """
    target = "0" * difficulty if difficulty > 0 else ""

    for position, block in enumerate(blocks):
        # Layer 1: Cryptographic Block Integrity
        recalculated = calculate_block_hash(block)
        if block["hash"] != recalculated:
            return False, f"[Integrity Failure] Block {position} contents tampered (hash mismatch)"

        if position > 0:
            expected_previous = blocks[position - 1]["hash"]
            if block["previous_hash"] != expected_previous:
                return False, f"[Integrity Failure] Block {position} broken linkage to previous block"

        if target and block.get("nonce", 0) > 0 and not block["hash"].startswith(target):
            return False, f"[Integrity Failure] Block {position} does not meet PoW target '{target}'"

        # Layer 2: Semantic Transaction Validity
        if check_transactions and position > 0:  # Skip genesis block course message
            for tx_idx, tx in enumerate(block.get("transactions", [])):
                is_valid, reason = validate_transaction(tx)
                if not is_valid:
                    return False, f"[Transaction Validity Failure] Block {position}, Tx {tx_idx}: {reason}"

    return True, "Chain passes all validation checks"
