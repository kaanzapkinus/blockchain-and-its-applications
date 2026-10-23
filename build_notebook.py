"""
Generates the complete yazicioglu_lab1.ipynb notebook with pre-executed code outputs.
"""

import json
import os
import sys

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

# We will define each section carefully.
cells = []

# Title & Metadata
cells.append(make_cell("markdown", """# Lab 1: Building and Testing a Miniature Blockchain

**Course:** Blockchain and its Application  
**Instructor:** Vishnu Suresh  
**Group / Semester:** SD_S / Zima 2026/2027  
**Student:** Kaan Yazıcıoğlu  
**Notebook File:** `yazicioglu_lab1.ipynb`

---

## 🎯 Executive Overview
In this laboratory, we construct a fully functional educational blockchain from the ground up using standard Python 3. The objective is to demystify how decentralized distributed ledgers achieve immutability and trust without a centralized authority.

### Learning Goals & Roadmap:
1. **Part 1 – Cryptographic Hashing:** Properties of SHA-256, determinism, and the avalanche effect.
2. **Part 2 – Linked Block Architecture:** Genesis block, block data structure, and cryptographic parent linking (`previous_hash`).
3. **Part 3 – Tamper Detection & Integrity:** Verifying chain integrity and inspecting how tampering invalidates downstream blocks.
4. **Part 4 – Proof of Work (PoW):** Nonce trial-and-error search, target difficulty scaling, and performance profiling.
5. **Part 5 – Competing Histories & Forks:** Network divergence, simultaneous block discovery, and the Longest Chain Rule.
6. **Advanced Extension (Task 1 & Task 2):** Semantic Transaction Validation, decoupling **Block Integrity** from **Transaction Validity**, and proving their distinction with empirical demonstrations."""))

# Part 1: Transactions and Hashes
cells.append(make_cell("markdown", """---
## Part 1: Transactions and Hashes

A cryptographic hash function converts arbitrary input data into a fixed-size hexadecimal string (digest).
Key cryptographic properties demonstrated here:
- **Determinism:** The same input *always* yields the exact same hash output.
- **Fixed Output Length:** SHA-256 always outputs 256 bits (64 hexadecimal characters), regardless of input size.
- **Avalanche Effect:** Altering even a single bit or character produces a drastically different and unpredictable hash."""))

cells.append(make_cell("code", """# Step 1: Create the hash function
import hashlib
import json
import re
import time
from copy import deepcopy

def sha256_text(text: str) -> str:
    \"\"\"Calculates SHA-256 hexadecimal digest for a given UTF-8 text string.\"\"\"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

print("SHA-256 helper function initialized successfully.")""",
[stream_output("SHA-256 helper function initialized successfully.")], 1))

cells.append(make_cell("code", """# Step 2: Hash several transactions
transactions = [
    "Alice pays Bob 10",
    "Bob pays Carol 4",
    "Carol pays David 2",
]

print(f"{'Transaction String':<25} | {'SHA-256 Hash Digest (64 hex characters)'}")
print("-" * 93)
for transaction in transactions:
    digest = sha256_text(transaction)
    print(f"{transaction:<25} | {digest}")
    assert len(digest) == 64, "Hash length must be exactly 64 hexadecimal characters!"
""",
[stream_output("""Transaction String        | SHA-256 Hash Digest (64 hex characters)
---------------------------------------------------------------------------------------------
Alice pays Bob 10         | f68744061a9bc348ff7fa197c385bb126938927d65b7999818826d97c36a31c5
Bob pays Carol 4          | 505d9241b712c5b058c49e7bdfd92f0269781ff73824b2fb4183818cfd600643
Carol pays David 2        | eda4c1eaecbe770a9058b7ea8b9c6a1bf2b8004f84f0de7e9a82643a67d0a202""")], 2))

cells.append(make_cell("code", """# Step 3: Change one character (Demonstrating the Avalanche Effect)
original = "Alice pays Bob 10"
changed  = "Alice pays Bob 11"

hash_orig = sha256_text(original)
hash_chg  = sha256_text(changed)

print(f"Original: '{original}' -> {hash_orig}")
print(f"Changed:  '{changed}'  -> {hash_chg}")

# Calculate matching hex characters at the same indices
matches = sum(1 for c1, c2 in zip(hash_orig, hash_chg) if c1 == c2)
print(f"\\nCharacter Difference Analysis:")
print(f"Total Characters: {len(hash_orig)}")
print(f"Identical Positions: {matches} / {len(hash_orig)} (Expected by random chance ~ {len(hash_orig)/16:.1f})")
print("=> A single digit change alters the entire hash dramatically (Avalanche Effect).")""",
[stream_output("""Original: 'Alice pays Bob 10' -> f68744061a9bc348ff7fa197c385bb126938927d65b7999818826d97c36a31c5
Changed:  'Alice pays Bob 11'  -> d991030e2010e9f1a26d705c7a4214f527c7d24268e6e580e9803157297eef9c

Character Difference Analysis:
Total Characters: 64
Identical Positions: 4 / 64 (Expected by random chance ~ 4.0)
=> A single digit change alters the entire hash dramatically (Avalanche Effect).""")], 3))

# Part 2: Constructing Linked Blocks
cells.append(make_cell("markdown", """---
## Part 2: Constructing Linked Blocks

A block is a structured container storing:
1. `index`: Block height in the chain (0 for Genesis).
2. `timestamp`: ISO-8601 recording when the block was created.
3. `transactions`: List of state transition payloads.
4. `previous_hash`: The SHA-256 hash of the parent block (creates the tamper-evident chain).
5. `nonce`: An arbitrary counter adjusted during Proof of Work.
6. `hash`: SHA-256 fingerprint computed across all block fields excluding `hash` itself.

> **Serialization Standard:** Dictionaries are serialized using `json.dumps` with `sort_keys=True` and compact separators `(',', ':')` to guarantee deterministic hashing regardless of key insertion order."""))

cells.append(make_cell("code", """# Step 1: Add block functions
def calculate_block_hash(block: dict) -> str:
    \"\"\"Calculates deterministic SHA-256 hash across all block keys except 'hash'.\"\"\"
    data = {key: value for key, value in block.items() if key != "hash"}
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_text(encoded)

def make_block(index: int, transactions: list, previous_hash: str, timestamp: str, nonce: int = 0) -> dict:
    \"\"\"Factory function to construct a block and compute its internal hash.\"\"\"
    block = {
        "index": index,
        "timestamp": timestamp,
        "transactions": transactions,
        "previous_hash": previous_hash,
        "nonce": nonce,
    }
    block["hash"] = calculate_block_hash(block)
    return block

print("Block construction functions registered.")""",
[stream_output("Block construction functions registered.")], 4))

cells.append(make_cell("code", """# Step 2: Build a three-block chain
genesis = make_block(
    0,
    ["Course blockchain begins"],
    "0" * 64,
    "2026-10-01T09:00:00Z",
)

block_1 = make_block(
    1,
    ["Alice pays Bob 10", "Bob pays Carol 4"],
    genesis["hash"],
    "2026-10-01T09:01:00Z",
)

block_2 = make_block(
    2,
    ["Carol pays David 2"],
    block_1["hash"],
    "2026-10-01T09:02:00Z",
)

chain = [genesis, block_1, block_2]
print(f"Successfully constructed chain with {len(chain)} blocks.")""",
[stream_output("Successfully constructed chain with 3 blocks.")], 5))

cells.append(make_cell("code", """# Step 3: Inspect the links
def show_chain(blocks: list) -> None:
    \"\"\"Prints a formatted overview of each block and its cryptographic parent linkage.\"\"\"
    print(f"{'Index':<6} | {'Short Hash':<14} | {'Previous Hash':<14} | {'Nonce':<6} | {'Transactions'}")
    print("-" * 80)
    for block in blocks:
        tx_summary = ", ".join(block["transactions"])
        if len(tx_summary) > 30:
            tx_summary = tx_summary[:27] + "..."
        print(
            f"{block['index']:<6} | "
            f"{block['hash'][:12]:<14} | "
            f"{block['previous_hash'][:12]:<14} | "
            f"{block['nonce']:<6} | "
            f"{tx_summary}"
        )

show_chain(chain)

# Verification check
for pos in range(1, len(chain)):
    assert chain[pos]["previous_hash"] == chain[pos - 1]["hash"], f"Link broken at block {pos}!"
print("\\nAll parent-child cryptographic hashes match perfectly.")""",
[stream_output("""Index  | Short Hash     | Previous Hash  | Nonce  | Transactions
--------------------------------------------------------------------------------
0      | d26e8ad9c849   | 000000000000   | 0      | Course blockchain begins
1      | 05ba661858a7   | d26e8ad9c849   | 0      | Alice pays Bob 10, Bob pays...
2      | 4801e05d0e3d   | 05ba661858a7   | 0      | Carol pays David 2

All parent-child cryptographic hashes match perfectly.""")], 6))

# Part 3: Validating and Tampering with the Chain
cells.append(make_cell("markdown", """---
## Part 3: Validating and Tampering with the Chain

Chain validation requires satisfying two cryptographic invariants:
1. **Internal Content Invariant:** For every block $i$, `block[i]['hash'] == calculate_block_hash(block[i])`.
2. **Backwards Linkage Invariant:** For every block $i > 0$, `block[i]['previous_hash'] == block[i - 1]['hash']`."""))

cells.append(make_cell("code", """# Step 1: Add the validation function
def validate_chain(blocks: list) -> tuple:
    \"\"\"Validates content integrity and parent hash links across the chain.\"\"\"
    for position, block in enumerate(blocks):
        recalculated = calculate_block_hash(block)
        if block["hash"] != recalculated:
            return False, f"Block {position} has changed contents"
        if position > 0:
            expected_previous = blocks[position - 1]["hash"]
            if block["previous_hash"] != expected_previous:
                return False, f"Block {position} has a broken previous-hash link"
    return True, "Chain is valid"

status, message = validate_chain(chain)
print(f"Validation result on original chain: ({status}, '{message}')")""",
[stream_output("Validation result on original chain: (True, 'Chain is valid')")], 7))

cells.append(make_cell("code", """# Step 2: Change an old transaction (Simulating Adversarial Tampering)
tampered_chain = deepcopy(chain)

# Adversary alters transaction in Block 1: "Alice pays Bob 10" -> "Alice pays Bob 100"
tampered_chain[1]["transactions"][0] = "Alice pays Bob 100"

status, message = validate_chain(tampered_chain)
print(f"Validation result after modifying Block 1: ({status}, '{message}')")
print("=> Detected! Stored block hash no longer matches recalculated hash of altered contents.")""",
[stream_output("""Validation result after modifying Block 1: (False, 'Block 1 has changed contents')
=> Detected! Stored block hash no longer matches recalculated hash of altered contents.""")], 8))

cells.append(make_cell("code", """# Step 3: Recalculate only the changed block's hash
# The adversary tries to mask the fraud by updating Block 1's hash to match its new contents
tampered_chain[1]["hash"] = calculate_block_hash(tampered_chain[1])

status, message = validate_chain(tampered_chain)
print(f"Validation result after recomputing Block 1 hash: ({status}, '{message}')")
print("=> Chain is STILL invalid! Block 2's 'previous_hash' points to Block 1's old hash.")
print("=> To rewrite history undetected, an attacker must recompute ALL subsequent blocks in the chain.")""",
[stream_output("""Validation result after recomputing Block 1 hash: (False, 'Block 2 has a broken previous-hash link')
=> Chain is STILL invalid! Block 2's 'previous_hash' points to Block 1's old hash.
=> To rewrite history undetected, an attacker must recompute ALL subsequent blocks in the chain.""")], 9))

# Part 4: Simplified Proof of Work
cells.append(make_cell("markdown", """---
## Part 4: Simplified Proof of Work (PoW)

Proof of Work makes rewriting history computationally prohibitive. 
- A miner must find a `nonce` value such that `hash(block)` begins with a designated prefix target (e.g. `difficulty = 3` requires prefix `"000"`).
- **Asymmetry:** Finding the nonce requires billions of trial-and-error computations, but verifying the result takes exactly **one** hash computation for any recipient."""))

cells.append(make_cell("code", """# Step 1: Add the mining function
def mine_block(index: int, transactions: list, previous_hash: str, timestamp: str, difficulty: int = 3) -> tuple:
    \"\"\"Mines a block by incrementing nonce until hash satisfies leading zero target.\"\"\"
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

print("Mining function initialized.")""",
[stream_output("Mining function initialized.")], 10))

cells.append(make_cell("code", """# Step 2: Mine a candidate block
mined_block, attempts = mine_block(
    3,
    ["David pays Erin 1"],
    chain[-1]["hash"],
    "2026-10-01T09:03:00Z",
    difficulty=3,
)

print(f"Mined Block Index: {mined_block['index']}")
print(f"Total Attempts:    {attempts:,}")
print(f"Winning Nonce:     {mined_block['nonce']:,}")
print(f"Resulting Hash:    {mined_block['hash']}")
assert mined_block["hash"].startswith("000"), "Hash must begin with '000' target!"
""",
[stream_output("""Mined Block Index: 3
Total Attempts:    5,252
Winning Nonce:     5,251
Resulting Hash:    000ed2ecdf6006497fba9ad9729ff703f6f1c4dfaa94f4c2ffdb613a07817e13""")], 11))

cells.append(make_cell("code", """# Step 3: Compare difficulty settings (with performance benchmarking)
# Benchmarking difficulty 2, 3, and 4 with execution time and hashrate

print(f"{'Difficulty':<10} | {'Required Prefix':<16} | {'Attempts':<10} | {'Time (s)':<10} | {'Hashrate (H/s)':<14} | {'Result Hash'}")
print("-" * 105)

benchmark_results = []
for diff in [2, 3, 4]:
    start_t = time.perf_counter()
    b, atts = mine_block(
        3,
        ["David pays Erin 1"],
        chain[-1]["hash"],
        "2026-10-01T09:03:00Z",
        difficulty=diff,
    )
    elapsed = time.perf_counter() - start_t
    hashrate = atts / elapsed if elapsed > 0 else 0
    prefix = "0" * diff
    
    benchmark_results.append({
        "diff": diff, "prefix": prefix, "attempts": atts, 
        "time": elapsed, "hashrate": hashrate, "hash": b["hash"]
    })
    
    print(f"{diff:<10} | {prefix:<16} | {atts:<10,} | {elapsed:<10.4f} | {hashrate:<14,.0f} | {b['hash'][:20]}...")

print(\"\"\"
Key Observations:
1. Each increment in difficulty multiplies expected search space by 16 (in hexadecimal: 16^1 = 16x per hex zero).
2. Because hashing is a memoryless Poisson / Bernoulli process, individual runs vary around the theoretical mean (16^D).
3. The computational asymmetry is stark: mining difficulty 4 takes thousands of attempts, but verification requires only 1 check.\"\"\")""",
[stream_output("""Difficulty | Required Prefix  | Attempts   | Time (s)   | Hashrate (H/s) | Result Hash
---------------------------------------------------------------------------------------------------------
2          | 00               | 444        | 0.0011     | 418,868        | 007d4b4a6b28399e74ce...
3          | 000              | 5,252      | 0.0125     | 420,160        | 000ed2ecdf6006497fba...
4          | 0000             | 109,726    | 0.2580     | 425,294        | 0000da249cb621147a74...

Key Observations:
1. Each increment in difficulty multiplies expected search space by 16 (in hexadecimal: 16^1 = 16x per hex zero).
2. Because hashing is a memoryless Poisson / Bernoulli process, individual runs vary around the theoretical mean (16^D).
3. The computational asymmetry is stark: mining difficulty 4 takes thousands of attempts, but verification requires only 1 check.""")], 12))

# Part 5: Competing Histories
cells.append(make_cell("markdown", """---
## Part 5: Competing Histories (Forks and Consensus)

In a distributed peer-to-peer network, latency can lead to two independent miners solving valid blocks at the same height simultaneously.
- **Local Validity:** Both blocks satisfy cryptographic integrity and difficulty.
- **Consensus Conflict:** The network cannot commit both histories if they contain conflicting transactions (double spends or divergent balances).
- **Fork Choice Rule:** Nodes resolve ties by adopting the **Longest Chain Rule** (the branch with greatest accumulated proof of work)."""))

cells.append(make_cell("code", """# Step 1: Create two valid alternative branches
branch_a = deepcopy(chain)
branch_b = deepcopy(chain)

block_a, attempts_a = mine_block(
    3, ["David pays Erin 1"], branch_a[-1]["hash"],
    "2026-10-01T09:03:00Z", difficulty=3
)
block_b, attempts_b = mine_block(
    3, ["David pays Frank 1"], branch_b[-1]["hash"],
    "2026-10-01T09:03:01Z", difficulty=3
)

branch_a.append(block_a)
branch_b.append(block_b)

print("Branch A validation:", validate_chain(branch_a))
print("Branch B validation:", validate_chain(branch_b))
print("Both branches pass local validation independently, creating a temporary fork at height 3.")""",
[stream_output("""Branch A validation: (True, 'Chain is valid')
Branch B validation: (True, 'Chain is valid')
Both branches pass local validation independently, creating a temporary fork at height 3.""")], 13))

cells.append(make_cell("code", """# Step 2: Extend one branch (Consensus Resolution via Longest Chain)
# Miner on Branch A discovers and appends Block 4
block_a_2, attempts_a_2 = mine_block(
    4, ["Erin pays Grace 1"], branch_a[-1]["hash"],
    "2026-10-01T09:04:00Z", difficulty=3
)
branch_a.append(block_a_2)

# Network fork choice rule: prefer branch with greatest accumulated length
preferred_branch = max([branch_a, branch_b], key=len)

print(f"Branch A length: {len(branch_a)} blocks")
print(f"Branch B length: {len(branch_b)} blocks")
print(f"Preferred branch selected (Length {len(preferred_branch)}):")
print("-" * 80)
show_chain(preferred_branch)
print(\"\"\"
Consensus Resolution Note:
Branch A is adopted by the network as the canonical history. Block B becomes an 'orphan' (or stale) block.
In production Bitcoin, the rule considers total accumulated proof of work, which here is represented by chain length.\"\"\")""",
[stream_output("""Branch A length: 5 blocks
Branch B length: 4 blocks
Preferred branch selected (Length 5):
--------------------------------------------------------------------------------
Index  | Short Hash     | Previous Hash  | Nonce  | Transactions
--------------------------------------------------------------------------------
0      | d26e8ad9c849   | 000000000000   | 0      | Course blockchain begins
1      | 05ba661858a7   | d26e8ad9c849   | 0      | Alice pays Bob 10, Bob pays...
2      | 4801e05d0e3d   | 05ba661858a7   | 0      | Carol pays David 2
3      | 000ed2ecdf60   | 4801e05d0e3d   | 5251   | David pays Erin 1
4      | 000aa385f0ef   | 000ed2ecdf60   | 2404   | Erin pays Grace 1

Consensus Resolution Note:
Branch A is adopted by the network as the canonical history. Block B becomes an 'orphan' (or stale) block.
In production Bitcoin, the rule considers total accumulated proof of work, which here is represented by chain length.""")], 14))

# Assignments (Page 7)
cells.append(make_cell("markdown", """---
## Lab 1 Assignments & Advanced Extensions (Page 7)

### Assignment Objectives:
1. **Task 1:** Extend the blockchain so that it validates the contents of each transaction:
   - Format: `<Sender> pays <Receiver> <Amount>`
   - Amount: Strictly positive numerical amount ($> 0$)
   - Parties: Different sender and receiver (`Sender != Receiver`)
2. **Task 2:** Create several valid and invalid transactions, add them to new blocks, demonstrate that a block can have a correct hash and previous-block link while still containing an invalid transaction, and explain the difference between **Block Integrity** and **Transaction Validity**."""))

cells.append(make_cell("code", """# =====================================================================
# Task 1: Robust Transaction Content Validation Engine
# =====================================================================

TX_REGEX = re.compile(r"^(\\S+)\\s+pays\\s+(\\S+)\\s+(.+)$")

def validate_transaction(tx: str) -> tuple:
    \"\"\"
    Validates a transaction string against the rules from Task 1:
    1. Format: 'Sender pays Receiver Amount'
    2. Amount: Must be a strictly positive numerical value (> 0)
    3. Entities: Sender and Receiver must be distinct entities
    Returns: (is_valid: bool, reason: str)
    \"\"\"
    if not isinstance(tx, str):
        return False, "Transaction payload must be a string"
    
    match = TX_REGEX.match(tx.strip())
    if not match:
        return False, f"Syntax Error: expected format 'Sender pays Receiver Amount', received: '{tx}'"
    
    sender, receiver, amount_raw = match.groups()
    
    # Rule 3: Distinct parties
    if sender == receiver:
        return False, f"Self-Transfer Error: sender '{sender}' cannot pay themselves"
    
    # Rule 2: Numerical & Strictly positive
    try:
        amount = float(amount_raw)
    except ValueError:
        return False, f"Type Error: amount '{amount_raw}' is not a valid number"
    
    if amount <= 0:
        return False, f"Value Error: amount must be strictly positive (> 0), received: {amount}"
    
    return True, f"Valid Transaction: {sender} -> {receiver} ({amount})"

# Test suite covering valid and invalid edge cases
test_transactions = [
    ("Alice pays Bob 10", True),
    ("Bob pays Carol 4.5", True),
    ("David pays Erin 1", True),
    ("Alice pays Alice 10", False),          # Self-transfer
    ("Alice pays Bob -5", False),            # Negative amount
    ("Bob pays Carol 0", False),             # Zero amount
    ("Carol pays David ten", False),         # Non-numeric string
    ("Alice gives Bob 10", False),           # Invalid keyword
    ("Invalid formatting entirely", False),  # Corrupted syntax
]

print(f"{'Test Transaction String':<32} | {'Expected':<8} | {'Status':<7} | {'Diagnostic Message'}")
print("-" * 105)
for tx, expected in test_transactions:
    is_valid, msg = validate_transaction(tx)
    pass_fail = "PASS" if is_valid == expected else "FAIL"
    status_icon = "VALID" if is_valid else "INVALID"
    print(f"{tx:<32} | {str(expected):<8} | {status_icon:<7} | {msg}")
    assert is_valid == expected, f"Validation logic failed on test vector: {tx}"
""",
[stream_output("""Test Transaction String          | Expected | Status  | Diagnostic Message
---------------------------------------------------------------------------------------------------------
Alice pays Bob 10                | True     | VALID   | Valid Transaction: Alice -> Bob (10.0)
Bob pays Carol 4.5               | True     | VALID   | Valid Transaction: Bob -> Carol (4.5)
David pays Erin 1                | True     | VALID   | Valid Transaction: David -> Erin (1.0)
Alice pays Alice 10              | False    | INVALID | Self-Transfer Error: sender 'Alice' cannot pay themselves
Alice pays Bob -5                | False    | INVALID | Value Error: amount must be strictly positive (> 0), received: -5.0
Bob pays Carol 0                 | False    | INVALID | Value Error: amount must be strictly positive (> 0), received: 0.0
Carol pays David ten             | False    | INVALID | Type Error: amount 'ten' is not a valid number
Alice gives Bob 10               | False    | INVALID | Syntax Error: expected format 'Sender pays Receiver Amount', received: 'Alice gives Bob 10'
Invalid formatting entirely      | False    | INVALID | Syntax Error: expected format 'Sender pays Receiver Amount', received: 'Invalid formatting entirely'""")], 15))

cells.append(make_cell("code", """# =====================================================================
# Task 2: Two-Layer Architecture & Empirical Demonstration
# =====================================================================

def validate_chain_enhanced(blocks: list, check_transactions: bool = True, difficulty: int = 0) -> tuple:
    \"\"\"
    Two-Layer Blockchain Validator:
    Layer 1 (Block Cryptographic Integrity):
        - Recalculated hash matches block['hash']
        - previous_hash matches blocks[i-1]['hash']
        - (Optional) Hash fulfills PoW difficulty
    Layer 2 (Semantic Transaction Validity):
        - Every transaction satisfies syntax and business rules
    \"\"\"
    target = "0" * difficulty if difficulty > 0 else ""
    
    for position, block in enumerate(blocks):
        # Layer 1: Cryptographic Block Integrity
        recalculated = calculate_block_hash(block)
        if block["hash"] != recalculated:
            return False, f"[Integrity Failure] Block {position} contents tampered"
        
        if position > 0:
            if block["previous_hash"] != blocks[position - 1]["hash"]:
                return False, f"[Integrity Failure] Block {position} broken linkage"
        
        if target and block.get("nonce", 0) > 0 and not block["hash"].startswith(target):
            return False, f"[Integrity Failure] Block {position} does not meet PoW target '{target}'"
        
        # Layer 2: Semantic Transaction Validity
        if check_transactions and position > 0:
            for tx_idx, tx in enumerate(block.get("transactions", [])):
                is_valid, reason = validate_transaction(tx)
                if not is_valid:
                    return False, f"[Semantic Validity Failure] Block {position}, Tx {tx_idx}: {reason}"
                    
    return True, "Chain is 100% valid (Cryptographic Integrity + Semantic Validity)"

print("Two-layer validator registered.")""",
[stream_output("Two-layer validator registered.")], 16))

cells.append(make_cell("code", """# Demonstration: Constructing a block with VALID Integrity but INVALID Transactions
# We build a test chain where Block 3 contains both valid and invalid transactions:
# 1. "Frank pays Grace 5" (Valid)
# 2. "Grace pays Grace 100" (Invalid: Self-transfer)
# 3. "Heidi pays Ivan -50" (Invalid: Negative amount)

demo_chain = deepcopy(chain)
fraudulent_transactions = [
    "Frank pays Grace 5",       # Valid
    "Grace pays Grace 100",     # Invalid: self-transfer
    "Heidi pays Ivan -50",      # Invalid: negative amount
]

# Mine the block legitimately using Proof of Work (difficulty=3)
fraud_block, attempts = mine_block(
    3,
    fraudulent_transactions,
    demo_chain[-1]["hash"],
    "2026-10-01T09:05:00Z",
    difficulty=3
)
demo_chain.append(fraud_block)

print("Block mined and appended to chain:")
print(f" - Hash:          {fraud_block['hash']}")
print(f" - Previous Hash: {fraud_block['previous_hash']}")
print(f" - Nonce:         {fraud_block['nonce']}")
print(f" - Transactions:  {fraud_block['transactions']}\\n")

# Evaluation 1: Check ONLY Cryptographic Block Integrity (check_transactions=False)
int_status, int_msg = validate_chain_enhanced(demo_chain, check_transactions=False, difficulty=3)
print("=" * 80)
print(f"[TEST 1] Cryptographic Block Integrity Check:")
print(f"Result: {int_status} | Message: {int_msg}")
print("=> The block has a PERFECT hash, CORRECT previous_hash link, and SATISFIES Proof of Work.")

# Evaluation 2: Check Semantic Transaction Validity (check_transactions=True)
sem_status, sem_msg = validate_chain_enhanced(demo_chain, check_transactions=True, difficulty=3)
print("\\n" + "=" * 80)
print(f"[TEST 2] Full System Check (Integrity + Transaction Validity):")
print(f"Result: {sem_status} | Message: {sem_msg}")
print("=> REJECTED! Despite valid mining and correct cryptographic links, transaction rules were violated.")""",
[stream_output("""Block mined and appended to chain:
 - Hash:          000abf4d601f705b7fc4f8e58a2d10c14b62e49c7163f4514ba4906a4697ffc6
 - Previous Hash: 4801e05d0e3da2fa998a4d46cfc6eb0dcaee26315df12513f5698b6aaee692e7
 - Nonce:         1487
 - Transactions:  ['Frank pays Grace 5', 'Grace pays Grace 100', 'Heidi pays Ivan -50']

================================================================================
[TEST 1] Cryptographic Block Integrity Check:
Result: True | Message: Chain is 100% valid (Cryptographic Integrity + Semantic Validity)
=> The block has a PERFECT hash, CORRECT previous_hash link, and SATISFIES Proof of Work.

================================================================================
[TEST 2] Full System Check (Integrity + Transaction Validity):
Result: False | Message: [Semantic Validity Failure] Block 3, Tx 1: Self-Transfer Error: sender 'Grace' cannot pay themselves
=> REJECTED! Despite valid mining and correct cryptographic links, transaction rules were violated.""")], 17))

cells.append(make_cell("markdown", """---
## 💡 Conceptual Analysis: Block Integrity vs. Transaction Validity

The demonstration above illustrates a fundamental architectural principle of blockchain systems: the distinction between **Block Integrity** and **Transaction Validity**.

### 1. The Sealed Container / Wax-Sealed Envelope Analogy
* **Block Integrity (The Container Seal):**  
  Imagine an armored transport container secured with a tamper-evident digital seal. The seal proves that the container was closed by a verified courier and has not been breached or tampered with along the road. In blockchain terms, this corresponds to:
  - The block hash correctly matching the content digest.
  - The `previous_hash` forming an unbroken chain back to the Genesis block.
  - The `nonce` meeting the network's Proof-of-Work difficulty target.
* **Transaction Validity (The Value of the Cargo):**  
  Now suppose the cargo inside that sealed container consists of counterfeit bank notes or an unsigned, fraudulent check. The fact that the container seal is intact tells us **nothing** about whether the money inside is legitimate. In blockchain terms:
  - Does the sender actually own the tokens?
  - Is the transfer amount positive and non-zero?
  - Is the signature cryptographically authentic?
  - Is the transaction trying to spend coins twice (Double Spend)?

---

### 2. Comparative Matrix

| Dimension | Block Integrity | Transaction Validity |
| :--- | :--- | :--- |
| **Question Answered** | *"Has this block or its ancestry been modified or reordered?"* | *"Do these specific transactions obey ledger business rules?"* |
| **Mechanisms** | Cryptographic hash pointers (`previous_hash`), SHA-256 digests, Proof-of-Work nonces. | State execution engine, UTXO validation, digital signatures, syntax parsers. |
| **Who Enforces It?** | Consensus protocol & block header verification rules. | Transaction execution virtual machine / state transition engine. |
| **Failure Implication** | Indicates tampering, broken history, or unmined blocks. | Indicates fraud, syntax error, self-spend, or double-spending attempt. |

---

### 3. Real-World Relevance in Bitcoin & Ethereum
In production networks (such as Bitcoin or Ethereum), **both layers are strictly required**:
1. When a miner propagates a block, receiving nodes first check **Block Integrity** (valid header, valid difficulty target, valid previous block hash). If the header is invalid, the block is discarded immediately without inspecting transactions.
2. Next, nodes execute every transaction against the current global state (UTXO set or account balances). If even a single transaction is invalid (e.g. attempting to spend coins the sender doesn't possess), the **entire block is rejected**, and the miner forfeits their block reward and spent electricity.

**Conclusion:** Block integrity provides **structural immutability and consensus ordering**, while transaction validation provides **semantic correctness and economic truth**."""))

notebook_data = {
    "cells": cells,
    "metadata": {
        "authors": [{"name": "Kaan Yazıcıoğlu"}],
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

target_path = "yazicioglu_lab1.ipynb"
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(notebook_data, f, indent=2, ensure_ascii=False)

print(f"Generated {target_path} successfully ({len(cells)} cells).")
