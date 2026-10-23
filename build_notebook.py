"""
Builds and runs the caveman-style notebook with user-requested names:
kaan, vishnu, alice, bob, satoshi, vitalik.
Captures live execution outputs directly into the notebook JSON.
"""

import hashlib
import json
import re
import time
from copy import deepcopy

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def calculate_block_hash(block: dict) -> str:
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

def validate_chain(blocks: list) -> tuple:
    for pos, b in enumerate(blocks):
        if b["hash"] != calculate_block_hash(b):
            return False, f"Block {pos} has changed contents"
        if pos > 0 and b["previous_hash"] != blocks[pos - 1]["hash"]:
            return False, f"Block {pos} has a broken previous-hash link"
    return True, "Chain is valid"

def mine_block(index: int, transactions: list, previous_hash: str, timestamp: str, difficulty: int = 3) -> tuple:
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

TX_PATTERN = re.compile(r"^(\S+)\s+pays\s+(\S+)\s+(.+)$")

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

def validate_chain_full(blocks: list, check_tx: bool = True) -> tuple:
    for pos, b in enumerate(blocks):
        if b["hash"] != calculate_block_hash(b):
            return False, f"Block {pos}: bad hash"
        if pos > 0 and b["previous_hash"] != blocks[pos - 1]["hash"]:
            return False, f"Block {pos}: broken link"
        if check_tx and pos > 0:
            for tx in b.get("transactions", []):
                ok, reason = validate_transaction(tx)
                if not ok:
                    return False, f"Block {pos} has invalid tx: '{tx}' ({reason})"
    return True, "All good"

# Helper for cells
def make_cell(cell_type, source, outputs=None, execution_count=None):
    if isinstance(source, str):
        source_lines = [line + "\n" for line in source.splitlines()]
        if source_lines and source.endswith("\n"):
            pass
        elif source_lines:
            source_lines[-1] = source_lines[-1].rstrip("\n")
    else:
        source_lines = source

    cell = {"cell_type": cell_type, "metadata": {}, "source": source_lines}
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

# RUN SIMULATION AND CAPTURE EXACT OUTPUTS
print("Running simulation with names: Kaan, Vishnu, Alice, Bob, Satoshi, Vitalik...")

# Cell 1: Imports
c1_out = "Ready."

# Cell 2: Transactions
c2_txs = ["Kaan pays Vishnu 10", "Satoshi pays Vitalik 4", "Alice pays Bob 2"]
c2_lines = []
for tx in c2_txs:
    c2_lines.append(f"{tx:<25} -> {sha256_text(tx)}")
c2_out = "\n".join(c2_lines)

# Cell 3: Avalanche
t1 = "Kaan pays Vishnu 10"
t2 = "Kaan pays Vishnu 11"
h1 = sha256_text(t1)
h2 = sha256_text(t2)
c3_out = f"Original: {h1}\nChanged:  {h2}\nSame length (64). Totally different hash. Avalanche effect."

# Cell 4: Linked Blocks
genesis = make_block(0, ["Course blockchain begins"], "0" * 64, "2026-10-01T09:00:00Z")
block_1 = make_block(1, ["Kaan pays Vishnu 10", "Satoshi pays Vitalik 4"], genesis["hash"], "2026-10-01T09:01:00Z")
block_2 = make_block(2, ["Alice pays Bob 2"], block_1["hash"], "2026-10-01T09:02:00Z")
chain = [genesis, block_1, block_2]

c4_lines = []
for b in chain:
    c4_lines.append(f"Block {b['index']} | hash: {b['hash'][:12]}.. | prev: {b['previous_hash'][:12]}.. | nonce: {b['nonce']}")
c4_out = "\n".join(c4_lines)

# Cell 5: Tamper
v_orig = validate_chain(chain)
bad_chain = deepcopy(chain)
bad_chain[1]["transactions"][0] = "Kaan pays Vishnu 100"
v_bad1 = validate_chain(bad_chain)
bad_chain[1]["hash"] = calculate_block_hash(bad_chain[1])
v_bad2 = validate_chain(bad_chain)
c5_out = f"Original chain: {v_orig}\nAfter edit tx:  {v_bad1}\nAfter fix hash: {v_bad2}\n-> Block 2 link breaks! Must rewrite whole chain to cheat."

# Cell 6: Mine block
mined_b3, atts3 = mine_block(3, ["Vitalik pays Kaan 1"], chain[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=3)
c6_out = f"Mined! Attempts: {atts3} | Nonce: {mined_b3['nonce']} | Hash: {mined_b3['hash']}"

# Cell 7: Difficulty compare
c7_lines = [
    f"{'Diff':<5} | {'Prefix':<7} | {'Attempts':<9} | {'Time (s)':<9} | {'Hash'}",
    "-" * 65
]
for diff in [2, 3, 4]:
    t0 = time.perf_counter()
    b, atts = mine_block(3, ["Vitalik pays Kaan 1"], chain[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=diff)
    dt = time.perf_counter() - t0
    c7_lines.append(f"{diff:<5} | {'0'*diff:<7} | {atts:<9} | {dt:<9.4f} | {b['hash'][:18]}..")
c7_lines.append("\nCaveman rule: each extra zero makes it ~16x harder.")
c7_out = "\n".join(c7_lines)

# Cell 8: Forks
branch_a = deepcopy(chain)
branch_b = deepcopy(chain)
b_a, _ = mine_block(3, ["Vitalik pays Kaan 1"], branch_a[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=3)
b_b, _ = mine_block(3, ["Vitalik pays Satoshi 1"], branch_b[-1]["hash"], "2026-10-01T09:03:01Z", difficulty=3)
branch_a.append(b_a)
branch_b.append(b_b)
v_a = validate_chain(branch_a)[0]
v_b = validate_chain(branch_b)[0]
b_a_2, _ = mine_block(4, ["Vishnu pays Alice 1"], branch_a[-1]["hash"], "2026-10-01T09:04:00Z", difficulty=3)
branch_a.append(b_a_2)
pref = max([branch_a, branch_b], key=len)

c8_lines = [
    f"Branch A valid: {v_a}",
    f"Branch B valid: {v_b}",
    f"Preferred chain length: {len(pref)} (Branch A won)"
]
for b in pref:
    c8_lines.append(f"Block {b['index']} | hash: {b['hash'][:12]}.. | prev: {b['previous_hash'][:12]}.. | nonce: {b['nonce']}")
c8_out = "\n".join(c8_lines)

# Cell 9: Task 1 tests
test_txs = [
    "Kaan pays Vishnu 10",
    "Satoshi pays Vitalik 4.5",
    "Alice pays Bob 1",
    "Kaan pays Kaan 10",
    "Satoshi pays Vitalik -5",
    "Vishnu pays Bob 0",
    "Vitalik pays Alice abc",
    "Random garbage text",
]
c9_lines = []
for t in test_txs:
    ok, msg = validate_transaction(t)
    c9_lines.append(f"[{'VALID' if ok else 'FAIL'}] {t:<26} -> {msg}")
c9_out = "\n".join(c9_lines)

# Cell 10: Task 2 demo
bad_tx_block, _ = mine_block(
    3,
    ["Kaan pays Kaan 100", "Satoshi pays Vitalik -50"],
    chain[-1]["hash"],
    "2026-10-01T09:05:00Z",
    difficulty=3
)
demo_chain = deepcopy(chain) + [bad_tx_block]
t1_res = validate_chain_full(demo_chain, check_tx=False)
t2_res = validate_chain_full(demo_chain, check_tx=True)
c10_out = f"""Test 1 - Check Block Integrity ONLY (check_tx=False):
Result: {t1_res}
-> Block hash and link are 100% CORRECT.

Test 2 - Check Full Chain WITH Transactions (check_tx=True):
Result: {t2_res}
-> REJECTED! Block is sealed, but payload inside is illegal."""

# BUILD CELLS
cells = []

cells.append(make_cell("markdown", """# Lab 1: Miniature Blockchain
**Course:** Blockchain & Application | **Instructor:** Vishnu Suresh | **Term:** Zima 2026/2027  
**Student:** Kaan Yazıcıoğlu | **File:** `yazicioglu_lab1.ipynb`

---
### Goal
Build small blockchain in Python. Test hashes, tamper detection, PoW mining, forks, and transaction checks."""))

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

print("Ready.")""", [stream_output(c1_out)], 1))

cells.append(make_cell("code", """transactions = [
    "Kaan pays Vishnu 10",
    "Satoshi pays Vitalik 4",
    "Alice pays Bob 2",
]

for tx in transactions:
    print(f"{tx:<25} -> {sha256_text(tx)}")""", [stream_output(c2_out)], 2))

cells.append(make_cell("code", """# Change 1 character: '10' -> '11'
t1 = "Kaan pays Vishnu 10"
t2 = "Kaan pays Vishnu 11"

print("Original:", sha256_text(t1))
print("Changed: ", sha256_text(t2))
print("Same length (64). Totally different hash. Avalanche effect.")""", [stream_output(c3_out)], 3))

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
block_1 = make_block(1, ["Kaan pays Vishnu 10", "Satoshi pays Vitalik 4"], genesis["hash"], "2026-10-01T09:01:00Z")
block_2 = make_block(2, ["Alice pays Bob 2"], block_1["hash"], "2026-10-01T09:02:00Z")

chain = [genesis, block_1, block_2]

def show_chain(blocks: list) -> None:
    for b in blocks:
        print(f"Block {b['index']} | hash: {b['hash'][:12]}.. | prev: {b['previous_hash'][:12]}.. | nonce: {b['nonce']}")

show_chain(chain)""", [stream_output(c4_out)], 4))

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
bad_chain[1]["transactions"][0] = "Kaan pays Vishnu 100"
print("After edit tx: ", validate_chain(bad_chain))

# Attack 2: recompute Block 1 hash to hide edit
bad_chain[1]["hash"] = calculate_block_hash(bad_chain[1])
print("After fix hash:", validate_chain(bad_chain))
print("-> Block 2 link breaks! Must rewrite whole chain to cheat.")""", [stream_output(c5_out)], 5))

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

mined_block, attempts = mine_block(3, ["Vitalik pays Kaan 1"], chain[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=3)
print(f"Mined! Attempts: {attempts} | Nonce: {mined_block['nonce']} | Hash: {mined_block['hash']}")""", [stream_output(c6_out)], 6))

cells.append(make_cell("code", """# Compare difficulty: 2, 3, 4
print(f"{'Diff':<5} | {'Prefix':<7} | {'Attempts':<9} | {'Time (s)':<9} | {'Hash'}")
print("-" * 65)

for diff in [2, 3, 4]:
    t0 = time.perf_counter()
    b, atts = mine_block(3, ["Vitalik pays Kaan 1"], chain[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=diff)
    dt = time.perf_counter() - t0
    print(f"{diff:<5} | {'0'*diff:<7} | {atts:<9} | {dt:<9.4f} | {b['hash'][:18]}..")

print("\\nCaveman rule: each extra zero makes it ~16x harder.")""", [stream_output(c7_out)], 7))

cells.append(make_cell("markdown", """---
## Part 5: Competing Histories (Forks)
Two miners find Block 3 at same time. Two valid chains.
Rule: longest chain wins."""))

cells.append(make_cell("code", """branch_a = deepcopy(chain)
branch_b = deepcopy(chain)

block_a, _ = mine_block(3, ["Vitalik pays Kaan 1"], branch_a[-1]["hash"], "2026-10-01T09:03:00Z", difficulty=3)
block_b, _ = mine_block(3, ["Vitalik pays Satoshi 1"], branch_b[-1]["hash"], "2026-10-01T09:03:01Z", difficulty=3)

branch_a.append(block_a)
branch_b.append(block_b)

print("Branch A valid:", validate_chain(branch_a)[0])
print("Branch B valid:", validate_chain(branch_b)[0])

# Miner on branch A finds Block 4
block_a_2, _ = mine_block(4, ["Vishnu pays Alice 1"], branch_a[-1]["hash"], "2026-10-01T09:04:00Z", difficulty=3)
branch_a.append(block_a_2)

# Pick longest
preferred = max([branch_a, branch_b], key=len)
print(f"Preferred chain length: {len(preferred)} (Branch A won)")
show_chain(preferred)""", [stream_output(c8_out)], 8))

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
    "Kaan pays Vishnu 10",
    "Satoshi pays Vitalik 4.5",
    "Alice pays Bob 1",
    "Kaan pays Kaan 10",
    "Satoshi pays Vitalik -5",
    "Vishnu pays Bob 0",
    "Vitalik pays Alice abc",
    "Random garbage text",
]

for t in tests:
    ok, msg = validate_transaction(t)
    print(f"[{'VALID' if ok else 'FAIL'}] {t:<26} -> {msg}")""", [stream_output(c9_out)], 9))

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
    ["Kaan pays Kaan 100", "Satoshi pays Vitalik -50"],
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
print("-> REJECTED! Block is sealed, but payload inside is illegal.")""", [stream_output(c10_out)], 10))

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
        "kernelspec": {"display_name": "Python (.venv)", "language": "python", "name": "blockchain-env"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open("yazicioglu_lab1.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_data, f, indent=2, ensure_ascii=False)

print("Generated yazicioglu_lab1.ipynb with custom names successfully.")
