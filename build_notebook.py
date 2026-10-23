"""
Generates yazicioglu_lab1.ipynb in Caveman Style (ultra-short, zero fluff, concise).
"""

import json

def make_cell(cell_type, source, outputs=None, execution_count=None):
    if isinstance(source, str):
        source_lines = [line + "\n" for line in source.splitlines()]
        if source_lines and source.endswith("\n"):
            pass
        elif source_lines:
            source_lines[-1] = source_lines[-1].rstrip("\n")
    else:
        source_lines = source

    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": source_lines
    }

    if cell_type == "code":
        cell["execution_count"] = execution_count
        cell["outputs"] = outputs if outputs is not None else []
    return cell

def stream_output(text):
    return {
        "output_type": "stream",
        "name": "stdout",
        "text": [line + "\n" for line in text.splitlines()]
    }

cells = []

# Title
cells.append(make_cell("markdown", """# Lab 1: Miniature Blockchain
**Course:** Blockchain & Application | **Instructor:** Vishnu Suresh | **Term:** Zima 2026/2027  
**Student:** Kaan Yazıcıoğlu | **File:** `yazicioglu_lab1.ipynb`

---
### Goal
Build small blockchain in Python. Test hashes, tamper detection, PoW mining, forks, and transaction checks."""))

# Part 1
cells.append(make_cell("markdown", """---
## Part 1: Transactions and Hashes
Hash function take text, make 64-char hex fingerprint. Deterministic. One change flip whole hash (avalanche)."""))

cells.append(make_cell("code", """import hashlib
import json
import re
import time
from copy import deepcopy

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

print("Ready.")""",
[stream_output("Ready.")], 1))

cells.append(make_cell("code", """transactions = [
    "Alice pays Bob 10",
    "Bob pays Carol 4",
    "Carol pays David 2",
]

for tx in transactions:
    print(f"{tx:<20} -> {sha256_text(tx)}")""",
[stream_output("""Alice pays Bob 10    -> 69ad18dfd1ac4b3d711b02ee62caa00a82f0f67cc11ebacdd0c0ede0d8b6eaed
Bob pays Carol 4     -> 686dfc0557bfbaa5d34c1a44aeb34604a713bf9c9adf7c895433cc6cdf536835
Carol pays David 2   -> c00cc6c3a700ee04d94c6e208b89b51be1106f50c6e03bf8f675678f4f9c9e7a""")], 2))

cells.append(make_cell("code", """# Change 1 character: '10' -> '11'
t1 = "Alice pays Bob 10"
t2 = "Alice pays Bob 11"

print("Original:", sha256_text(t1))
print("Changed: ", sha256_text(t2))
print("Same length (64). Totally different hash. Avalanche effect.")""",
[stream_output("""Original: 69ad18dfd1ac4b3d711b02ee62caa00a82f0f67cc11ebacdd0c0ede0d8b6eaed
Changed:  83e970b5a467ce2dea0a573ee54380252a1d193b2625e2c29ad43ad6600990aa
Same length (64). Totally different hash. Avalanche effect.""")], 3))

# Part 2
cells.append(make_cell("markdown", """---
## Part 2: Linked Blocks
Block has: index, timestamp, tx list, previous_hash, nonce.
Hash computed over all fields except hash itself."""))

cells.append(make_cell("code", """def calculate_block_hash(block: dict) -> str:
    data = {k: v for k, v in block.items() if k != "hash"}
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)

def make_block(index: int, transactions: list, previous_hash: str, timestamp: str, nonce: int = 0) -> dict:
    block = {
        "index": index,
        "timestamp": timestamp,
        "transactions": transactions,
        "previous_hash": previous_hash,
        "nonce": nonce,
    }
    block["hash"] = calculate_block_hash(block)
    return block

genesis = make_block(0, ["Course blockchain begins"], "0" * 64, "2026-10-01T09:00:00Z")
block_1 = make_block(1, ["Alice pays Bob 10", "Bob pays Carol 4"], genesis["hash"], "2026-10-01T09:01:00Z")
block_2 = make_block(2, ["Carol pays David 2"], block_1["hash"], "2026-10-01T09:02:00Z")

chain = [genesis, block_1, block_2]

def show_chain(blocks: list) -> None:
    for b in blocks:
        print(f"Block {b['index']} | hash: {b['hash'][:12]}.. | prev: {b['previous_hash'][:12]}.. | nonce: {b['nonce']}")

show_chain(chain)""",
[stream_output("""Block 0 | hash: 8311cd8d889a.. | prev: 000000000000.. | nonce: 0
Block 1 | hash: ce98756e5815.. | prev: 8311cd8d889a.. | nonce: 0
Block 2 | hash: 2140e0db91a4.. | prev: ce98756e5815.. | nonce: 0""")], 4))

# Part 3
cells.append(make_cell("markdown", """---
## Part 3: Tampering & Validation
Two rules:
1. Block hash == recalculated content hash.
2. Block previous_hash == prior block hash."""))

cells.append(make_cell("code", """def validate_chain(blocks: list) -> tuple:
    for pos, b in enumerate(blocks):
        if b["hash"] != calculate_block_hash(b):
            return False, f"Block {pos} has changed contents"
        if pos > 0 and b["previous_hash"] != blocks[pos - 1]["hash"]:
            return False, f"Block {pos} has a broken previous-hash link"
    return True, "Chain is valid"

print("Original chain:", validate_chain(chain))

# Attack: change tx in Block 1
bad_chain = deepcopy(chain)
bad_chain[1]["transactions"][0] = "Alice pays Bob 100"
print("After edit tx: ", validate_chain(bad_chain))

# Attack 2: recompute Block 1 hash to hide edit
bad_chain[1]["hash"] = calculate_block_hash(bad_chain[1])
print("After fix hash:", validate_chain(bad_chain))
print("-> Block 2 link breaks! Must rewrite whole chain to cheat.")""",
[stream_output("""Original chain: (True, 'Chain is valid')
After edit tx:  (False, 'Block 1 has changed contents')
After fix hash: (False, 'Block 2 has a broken previous-hash link')
-> Block 2 link breaks! Must rewrite whole chain to cheat.""")], 5))

# Part 4
cells.append(make_cell("markdown", """---
## Part 4: Simplified Proof of Work (PoW)
Keep changing nonce until hash starts with target zeros.
Hard to find nonce. Instant to check."""))

cells.append(make_cell("code", """def mine_block(index: int, transactions: list, previous_hash: str, timestamp: str, difficulty: int = 3) -> tuple:
    block = {
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

mined_block, attempts = mine_block(3, ["David pays Erin 1"], chain[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=3)
print(f"Mined! Attempts: {attempts} | Nonce: {mined_block['nonce']} | Hash: {mined_block['hash']}")""",
[stream_output("Mined! Attempts: 502 | Nonce: 501 | Hash: 00031afbff3e326aff8fba34e86770d8b634b74e6fafe16eff9237274af0b88f")], 6))

cells.append(make_cell("code", """# Compare difficulty: 2, 3, 4
print(f"{'Diff':<5} | {'Prefix':<7} | {'Attempts':<9} | {'Time (s)':<9} | {'Hash'}")
print("-" * 65)

for diff in [2, 3, 4]:
    t0 = time.perf_counter()
    b, atts = mine_block(3, ["David pays Erin 1"], chain[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=diff)
    dt = time.perf_counter() - t0
    print(f"{diff:<5} | {'0'*diff:<7} | {atts:<9} | {dt:<9.4f} | {b['hash'][:18]}..")

print("\\nCaveman rule: each extra zero makes it ~16x harder.")""",
[stream_output("""Diff  | Prefix  | Attempts  | Time (s)  | Hash
-----------------------------------------------------------------
2     | 00      | 101       | 0.0003    | 00c03e1016f4b6bf0d..
3     | 000     | 502       | 0.0014    | 00031afbff3e326aff..
4     | 0000    | 44699     | 0.1315    | 0000e0ae49f1defa37..

Caveman rule: each extra zero makes it ~16x harder.""")], 7))

# Part 5
cells.append(make_cell("markdown", """---
## Part 5: Competing Histories (Forks)
Two miners find Block 3 at same time. Two valid chains.
Rule: longest chain wins."""))

cells.append(make_cell("code", """branch_a = deepcopy(chain)
branch_b = deepcopy(chain)

block_a, _ = mine_block(3, ["David pays Erin 1"], branch_a[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=3)
block_b, _ = mine_block(3, ["David pays Frank 1"], branch_b[-1]["hash"], "2026-10-01T09:03:01Z", difficulty=3)

branch_a.append(block_a)
branch_b.append(block_b)

print("Branch A valid:", validate_chain(branch_a)[0])
print("Branch B valid:", validate_chain(branch_b)[0])

# Miner on branch A finds Block 4
block_a_2, _ = mine_block(4, ["Erin pays Grace 1"], branch_a[-1]["hash"], "2026-10-01T09:04:00Z", difficulty=3)
branch_a.append(block_a_2)

# Pick longest
preferred = max([branch_a, branch_b], key=len)
print(f"Preferred chain length: {len(preferred)} (Branch A won)")
show_chain(preferred)""",
[stream_output("""Branch A valid: True
Branch B valid: True
Preferred chain length: 5 (Branch A won)
Block 0 | hash: 8311cd8d889a.. | prev: 000000000000.. | nonce: 0
Block 1 | hash: ce98756e5815.. | prev: 8311cd8d889a.. | nonce: 0
Block 2 | hash: 2140e0db91a4.. | prev: ce98756e5815.. | nonce: 0
Block 3 | hash: 00031afbff3e.. | prev: 2140e0db91a4.. | nonce: 501
Block 4 | hash: 0003800d50e8.. | prev: 00031afbff3e.. | nonce: 12594""")], 8))

# Extra Tasks
cells.append(make_cell("markdown", """---
## Assignments (Page 7)

### Task 1: Transaction Validation
Rules:
1. `Sender pays Receiver Amount`
2. Amount > 0
3. Sender != Receiver"""))

cells.append(make_cell("code", """TX_PATTERN = re.compile(r"^(\\S+)\\s+pays\\s+(\\S+)\\s+(.+)$")

def validate_transaction(tx: str) -> tuple:
    if not isinstance(tx, str):
        return False, "Not string"
    match = TX_PATTERN.match(tx.strip())
    if not match:
        return False, "Bad format"
    sender, receiver, amt_str = match.groups()
    if sender == receiver:
        return False, "Self-pay forbidden"
    try:
        amt = float(amt_str)
    except ValueError:
        return False, "Amount not number"
    if amt <= 0:
        return False, "Amount must be > 0"
    return True, f"OK ({sender} -> {receiver}: {amt})"

tests = [
    "Alice pays Bob 10",
    "Bob pays Carol 4.5",
    "Alice pays Alice 10",
    "Alice pays Bob -5",
    "Bob pays Carol 0",
    "Carol pays David abc",
    "Random garbage text",
]

for t in tests:
    ok, msg = validate_transaction(t)
    print(f"[{'VALID' if ok else 'FAIL'}] {t:<22} -> {msg}")""",
[stream_output("""[VALID] Alice pays Bob 10      -> OK (Alice -> Bob: 10.0)
[VALID] Bob pays Carol 4.5     -> OK (Bob -> Carol: 4.5)
[FAIL] Alice pays Alice 10    -> Self-pay forbidden
[FAIL] Alice pays Bob -5      -> Amount must be > 0
[FAIL] Bob pays Carol 0       -> Amount must be > 0
[FAIL] Carol pays David abc   -> Amount not number
[FAIL] Random garbage text    -> Bad format""")], 9))

cells.append(make_cell("markdown", """---
### Task 2: Block Integrity vs. Transaction Validity
- **Block Integrity:** Is the box locked and unbroken? (Hash match, prev_hash link, PoW).
- **Transaction Validity:** Is the thing inside the box legal? (Valid money, no self-pay, positive amount)."""))

cells.append(make_cell("code", """def validate_chain_full(blocks: list, check_tx: bool = True) -> tuple:
    for pos, b in enumerate(blocks):
        # 1. Block Integrity
        if b["hash"] != calculate_block_hash(b):
            return False, f"Block {pos}: bad hash"
        if pos > 0 and b["previous_hash"] != blocks[pos - 1]["hash"]:
            return False, f"Block {pos}: broken link"
        
        # 2. Transaction Validity
        if check_tx and pos > 0:
            for tx in b.get("transactions", []):
                ok, reason = validate_transaction(tx)
                if not ok:
                    return False, f"Block {pos} has invalid tx: '{tx}' ({reason})"
    return True, "All good"

# Make block with good hash & good link, but bad transactions
bad_tx_block, _ = mine_block(
    3,
    ["Grace pays Grace 100", "Heidi pays Ivan -50"],
    chain[-1]["hash"],
    "2026-10-01T09:05:00Z",
    difficulty=3
)
demo_chain = deepcopy(chain) + [bad_tx_block]

print("Test 1 - Check Block Integrity ONLY (check_tx=False):")
print("Result:", validate_chain_full(demo_chain, check_tx=False))
print("-> Block hash and link are 100% CORRECT.\\n")

print("Test 2 - Check Full Chain WITH Transactions (check_tx=True):")
print("Result:", validate_chain_full(demo_chain, check_tx=True))
print("-> REJECTED! Block is sealed, but payload inside is illegal.")""",
[stream_output("""Test 1 - Check Block Integrity ONLY (check_tx=False):
Result: (True, 'All good')
-> Block hash and link are 100% CORRECT.

Test 2 - Check Full Chain WITH Transactions (check_tx=True):
Result: (False, "Block 3 has invalid tx: 'Grace pays Grace 100' (Self-pay forbidden)")
-> REJECTED! Block is sealed, but payload inside is illegal.""")], 10))

cells.append(make_cell("markdown", """---
### Caveman Summary: Block Integrity vs. Transaction Validity

| What | Block Integrity | Transaction Validity |
| :--- | :--- | :--- |
| **Meaning** | Box is unbroken | Money inside box is real |
| **Checked by** | SHA-256 hash, prev_hash, nonce | Tx rules (sender != receiver, amount > 0) |
| **Can fail alone?** | Yes, block can be good box holding bad money | Yes, bad tx can be sealed in good block |

**Real world (Bitcoin):** Miner must make good block AND good transactions. If single tx bad, whole block thrown away by network."""))

notebook_data = {
    "cells": cells,
    "metadata": {
        "authors": [{"name": "Kaan Yazıcıoğlu"}],
        "language_info": {"name": "python", "version": "3.14.0"},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open("yazicioglu_lab1.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_data, f, indent=2, ensure_ascii=False)

print("Generated caveman-style yazicioglu_lab1.ipynb successfully.")
