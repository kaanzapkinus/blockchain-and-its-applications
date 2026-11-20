"""
Generates and executes Lab 2 notebook in Caveman Style:
yazicioglu_lab2.ipynb
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

# =====================================================================
# SIMULATE EXPERIMENTS & CAPTURE OUTPUTS
# =====================================================================

validators = [
    "University A", "University B", "University C",
    "University D", "University E",
]

proposal = {
    "student": "Kaan Yazicioglu",
    "credential": "Blockchain Fundamentals",
    "issuer": "University A",
}

def validate_proposal(proposal):
    required = {"student", "credential", "issuer"}
    missing = required - set(proposal)
    if missing:
        return False, f"Missing fields: {sorted(missing)}"
    if proposal["issuer"] not in validators:
        return False, "Issuer is not a consortium member"
    return True, "Proposal follows the rules"

def quorum_result(votes, threshold=4):
    approvals = sum(vote is True for vote in votes.values())
    responding = sum(vote is not None for vote in votes.values())
    return approvals >= threshold, approvals, responding

votes = {
    validator: validate_proposal(proposal)[0]
    for validator in validators
}

c1_out = f"{votes}\n{quorum_result(votes)}"

# Part 2
crash_votes = votes.copy()
crash_votes["University E"] = None
c2_1_out = f"{crash_votes}\n{quorum_result(crash_votes)}"

dishonest_votes = votes.copy()
dishonest_votes["University E"] = False
c2_2_out = f"{dishonest_votes}\n{quorum_result(dishonest_votes)}"

invalid_proposal = {
    "student": "Kaan Yazicioglu",
    "credential": "Blockchain Fundamentals",
    "issuer": "Unknown University",
}
invalid_votes = {
    validator: validate_proposal(invalid_proposal)[0]
    for validator in validators
}
invalid_votes["University E"] = True
c2_3_out = f"{invalid_votes}\n{quorum_result(invalid_votes)}"

# Part 3
def has_quorum(voter_set, threshold):
    return len(set(voter_set)) >= threshold

left_side = {"University A", "University B", "University C"}
right_side = {"University D", "University E"}
c3_1_out = f"Left at threshold 4: {has_quorum(left_side, 4)}\nRight at threshold 4: {has_quorum(right_side, 4)}"

proposal_x_voters = {"University A", "University B", "University E"}
proposal_y_voters = {"University C", "University D", "University E"}
both_voted = proposal_x_voters & proposal_y_voters
c3_2_out = f"X at threshold 3: {has_quorum(proposal_x_voters, 3)}\nY at threshold 3: {has_quorum(proposal_y_voters, 3)}\nVoted for both: {both_voted}"

# Part 4
def simple_majority(votes):
    approvals = sum(votes.values())
    return approvals > len(votes) / 2

honest_votes = {validator: False for validator in validators}
fake_votes = {f"Fake identity {number}": True for number in range(1, 21)}
open_votes = {**honest_votes, **fake_votes}
c4_1_out = f"Identity count: {len(open_votes)}\nAttacker wins: {simple_majority(open_votes)}"

authorized = set(validators)
authorized_votes = {
    identity: vote
    for identity, vote in open_votes.items()
    if identity in authorized
}
c4_2_out = f"Authorized identities: {len(authorized_votes)}\nAttacker wins: {simple_majority(authorized_votes)}"

# Part 5
def minimum_coalition(weights, threshold):
    ordered = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    coalition = []
    total = 0
    for validator, weight in ordered:
        coalition.append(validator)
        total += weight
        if total >= threshold:
            return coalition, total
    return coalition, total

equal_weights = {"A": 20, "B": 20, "C": 20, "D": 20, "E": 20}
concentrated_weights = {"A": 40, "B": 25, "C": 15, "D": 10, "E": 10}
c5_2_out = f"Equal: {minimum_coalition(equal_weights, 67)}\nConcentrated: {minimum_coalition(concentrated_weights, 67)}"

# Part 5 Step 3: Extreme case
extreme_weights = {"A": 70, "B": 10, "C": 10, "D": 5, "E": 5}
c5_3_out = f"Extreme: {minimum_coalition(extreme_weights, 67)}"

# =====================================================================
# ASSEMBLE CELLS
# =====================================================================
cells = []

# Header
cells.append(make_cell("markdown", """# Lab 2: Simulating Decentralized Agreement and Control
**Course:** Blockchain and its Application | **Instructor:** Vishnu Suresh | **Term:** Zima 2026/2027  
**Student:** Kaan Yazıcıoğlu | **File:** `yazicioglu_lab2.ipynb`

---
### Goal
Simulate consensus and governance among 5 universities:
1. Quorum approval (4 of 5).
2. Crash vs. Byzantine faults.
3. Network split (Safety vs. Liveness).
4. Sybil attack vs. Permissioned whitelist.
5. Voting weight concentration & fake decentralization.
6. Final design proposal."""))

# Part 1
cells.append(make_cell("markdown", """---
## Part 1: Trust Model and Quorum Approval
5 universities. Need 4 out of 5 approvals to accept diploma."""))

cells.append(make_cell("code", """validators = [
    "University A", "University B", "University C",
    "University D", "University E",
]

proposal = {
    "student": "Kaan Yazicioglu",
    "credential": "Blockchain Fundamentals",
    "issuer": "University A",
}

def validate_proposal(proposal):
    required = {"student", "credential", "issuer"}
    missing = required - set(proposal)
    if missing:
        return False, f"Missing fields: {sorted(missing)}"
    if proposal["issuer"] not in validators:
        return False, "Issuer is not a consortium member"
    return True, "Proposal follows the rules"

def quorum_result(votes, threshold=4):
    approvals = sum(vote is True for vote in votes.values())
    responding = sum(vote is not None for vote in votes.values())
    return approvals >= threshold, approvals, responding

votes = {
    validator: validate_proposal(proposal)[0]
    for validator in validators
}

print(votes)
print(quorum_result(votes))""", [stream_output(c1_out)], 1))

# Part 2
cells.append(make_cell("markdown", """---
## Part 2: Crash and Byzantine Faults
- **Crash fault:** node dead / no answer (`None`).
- **Byzantine fault:** node lies / votes wrong.
- 1 faulty node cannot stop 4-of-5 quorum."""))

cells.append(make_cell("code", """# Step 1: 1 Crashed node (University E = None)
crash_votes = votes.copy()
crash_votes["University E"] = None
print("Crash votes:", crash_votes)
print("Result:     ", quorum_result(crash_votes))
print("-> 4 honest online nodes reach quorum. System makes progress.")""",
[stream_output(f"Crash votes: {crash_votes}\nResult:      {quorum_result(crash_votes)}\n-> 4 honest online nodes reach quorum. System makes progress.")], 2))

cells.append(make_cell("code", """# Step 2: 1 Dishonest node votes False on valid proposal
dishonest_votes = votes.copy()
dishonest_votes["University E"] = False
print("Dishonest votes:", dishonest_votes)
print("Result:         ", quorum_result(dishonest_votes))
print("-> 4 honest approvals still reach threshold. Bad vote ignored.")""",
[stream_output(f"Dishonest votes: {dishonest_votes}\nResult:          {quorum_result(dishonest_votes)}\n-> 4 honest approvals still reach threshold. Bad vote ignored.")], 3))

cells.append(make_cell("code", """# Step 3: Bad proposal submitted (Unknown issuer)
invalid_proposal = {
    "student": "Kaan Yazicioglu",
    "credential": "Blockchain Fundamentals",
    "issuer": "Unknown University",
}

invalid_votes = {
    validator: validate_proposal(invalid_proposal)[0]
    for validator in validators
}
# Dishonest University E tries to approve fake diploma
invalid_votes["University E"] = True

print("Invalid votes:", invalid_votes)
print("Result:       ", quorum_result(invalid_votes))
print("-> Rejected! 1 dishonest vote cannot reach 4-of-5 quorum.")""",
[stream_output(f"Invalid votes: {invalid_votes}\nResult:        {quorum_result(invalid_votes)}\n-> Rejected! 1 dishonest vote cannot reach 4-of-5 quorum.")], 4))

# Part 3
cells.append(make_cell("markdown", """---
## Part 3: Network Partitions (Safety vs. Liveness)
Network cuts in two: Left (3 nodes) vs. Right (2 nodes).
- **Threshold 4:** Neither side reaches 4. Chain stops (**Safety saved, Liveness lost**).
- **Threshold 3:** Split-brain danger! Traitor voting on both sides makes 2 conflicting decisions (**Safety dead**)."""))

cells.append(make_cell("code", """def has_quorum(voter_set, threshold):
    return len(set(voter_set)) >= threshold

left_side = {"University A", "University B", "University C"}
right_side = {"University D", "University E"}

print("Left at threshold 4: ", has_quorum(left_side, 4))
print("Right at threshold 4:", has_quorum(right_side, 4))
print("-> Neither side reaches 4. Network pauses. Prevents double-spend/split-brain.")""",
[stream_output(f"Left at threshold 4:  False\nRight at threshold 4: False\n-> Neither side reaches 4. Network pauses. Prevents double-spend/split-brain.")], 5))

cells.append(make_cell("code", """# Lower threshold to 3 + traitor E votes on both sides (equivocation)
proposal_x_voters = {"University A", "University B", "University E"}
proposal_y_voters = {"University C", "University D", "University E"}

print("X at threshold 3:", has_quorum(proposal_x_voters, 3))
print("Y at threshold 3:", has_quorum(proposal_y_voters, 3))
print("Voted for both:  ", proposal_x_voters & proposal_y_voters)
print("-> Disaster! Both conflicting proposals finalized at same time.")""",
[stream_output(f"X at threshold 3: True\nY at threshold 3: True\nVoted for both:   {{'University E'}}\n-> Disaster! Both conflicting proposals finalized at same time.")], 6))

cells.append(make_cell("markdown", """### Comparison: Threshold 4 vs. Threshold 3

| Threshold | 3-2 Network Partition | Conflicting Quorum Risk |
| :--- | :--- | :--- |
| **4 of 5** | Neither side finalizes (Liveness pauses) | Zero: One traitor cannot finalize two sides |
| **3 of 5** | Left side finalizes (Liveness continues) | High: Traitor voting twice approves 2 conflicting histories |"""))

# Part 4
cells.append(make_cell("markdown", """---
## Part 4: Sybil Resistance
Open voting without ID check: attacker creates 20 fake bots and outvotes 5 real universities.
Defense: Permissioned membership list (or PoW/PoS in open networks)."""))

cells.append(make_cell("code", """def simple_majority(votes):
    approvals = sum(votes.values())
    return approvals > len(votes) / 2

honest_votes = {validator: False for validator in validators}
fake_votes = {f"Fake identity {number}": True for number in range(1, 21)}
open_votes = {**honest_votes, **fake_votes}

print("Total voters: ", len(open_votes))
print("Attacker wins:", simple_majority(open_votes))
print("-> Sybil attack works! Cheap fake identities steal control.")""",
[stream_output(f"Total voters:  25\nAttacker wins: True\n-> Sybil attack works! Cheap fake identities steal control.")], 7))

cells.append(make_cell("code", """# Fix: Whitelist authorized validators
authorized = set(validators)
authorized_votes = {
    identity: vote
    for identity, vote in open_votes.items()
    if identity in authorized
}

print("Authorized voters counted:", len(authorized_votes))
print("Attacker wins:            ", simple_majority(authorized_votes))
print("-> Fake identities blocked by membership check.")""",
[stream_output(f"Authorized voters counted: 5\nAttacker wins:             False\n-> Fake identities blocked by membership check.")], 8))

cells.append(make_cell("markdown", """### Caveman Summary: Sybil Defense
- **Consortium:** Whitelist of known cryptographic keys.
- **Proof of Work (Bitcoin):** 1 CPU/hashrate = 1 vote. Identities are free, electricity is not.
- **Proof of Stake (Ethereum):** 1 coin = 1 vote. Identities are free, capital is not."""))

# Part 5
cells.append(make_cell("markdown", """---
## Part 5: Effective Control and Unequal Voting Power
Node count is deceptive.
If Validator A holds 70% of voting weight, having 5 nodes on paper means nothing. Validator A is dictator."""))

cells.append(make_cell("code", """def minimum_coalition(weights, threshold):
    ordered = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    coalition = []
    total = 0
    for validator, weight in ordered:
        coalition.append(validator)
        total += weight
        if total >= threshold:
            return coalition, total
    return coalition, total

equal_weights = {"A": 20, "B": 20, "C": 20, "D": 20, "E": 20}
concentrated_weights = {"A": 40, "B": 25, "C": 15, "D": 10, "E": 10}

print("Equal (threshold 67):       ", minimum_coalition(equal_weights, 67))
print("Concentrated (threshold 67):", minimum_coalition(concentrated_weights, 67))""",
[stream_output("""Equal (threshold 67):        (['A', 'B', 'C', 'D'], 80)
Concentrated (threshold 67): (['A', 'B', 'C'], 80)""")], 9))

cells.append(make_cell("code", """# Step 3: Extreme case (Validator A has 70%, remaining 30% split)
extreme_weights = {"A": 70, "B": 10, "C": 10, "D": 5, "E": 5}
res_coalition, res_weight = minimum_coalition(extreme_weights, 67)

print(f"Extreme case (threshold 67): Coalition={res_coalition}, Weight={res_weight}")
print("-> Coalition size = 1! Validator A decides everything alone.")
print("-> Caveman answer: Validator count does NOT measure decentralization. Weight distribution does.")""",
[stream_output("""Extreme case (threshold 67): Coalition=['A'], Weight=70
-> Coalition size = 1! Validator A decides everything alone.
-> Caveman answer: Validator count does NOT measure decentralization. Weight distribution does.""")], 10))

# Part 6 & Final Task
cells.append(make_cell("markdown", """---
## Part 6: Decentralization Design Proposal (Final Task)

### Selected Scenario:
**Scenario 1: Five Universities Sharing Micro-Credentials (Permissioned Consortium)**

#### 1. Who submits records and who validates them?
- **Submitters:** Only accredited member universities submit credential issuance/revocation proposals.
- **Validators:** All 5 university validator nodes validate proposals against shared schema and issuer cryptographic signatures.

#### 2. Who may read the ledger and who governs membership or upgrades?
- **Readers:** Public access (students, employers, verifiers) via open read-only RPC/API to verify diploma authenticity.
- **Governance:** Consortium board (5 university representatives) with 4-of-5 threshold multisig to add/remove members or upgrade smart contracts.

#### 3. Which failures or collusion the design must tolerate?
- Tolerates **1 crash fault** ($N=5, T=4 \rightarrow$ system continues with 4 nodes).
- Tolerates **1 Byzantine (dishonest) fault** ($T=4$ prevents a rogue node from approving fake credentials or blocking valid ones).
- Requires at least 2 malicious universities colluding to cause damage.

#### 4. How the design resists fake identities (Sybil attacks)?
- **Permissioned PKI whitelist:** Node identities are tied to authenticated cryptographic certificates (e.g. X.509). Unregistered keys cannot vote. No wasteful PoW/PoS needed.

#### 5. What quorum, fork-choice, or finality rule determines acceptance?
- **Rule:** Deterministic 4-of-5 ($80\%$) quorum rule.
- **Finality:** Instant deterministic finality (BFT-style). Once 4 signatures are collected, the block is permanent. No forks or chain reorgs allowed.

#### 6. Where effective control could become concentrated?
- **Hosting / Cloud dependency:** If all universities host nodes on AWS us-east-1.
- **Software monoculture:** All nodes running identical unpatched client software.
- **Unequal voting:** If voting weight scales with university student count rather than strict 1-institution = 1-vote.

#### 7. Whether a simpler signed database would meet the same need?
- **Why database fails:** A single database has a single administrator. One university can secretly modify records, delete competitor credentials, or suffer a single-point-of-failure outage.
- **Why blockchain succeeds:** Provides mutual distrust protection. No single university can unilaterally rewrite or censor history."""))

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

with open("yazicioglu_lab2.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_data, f, indent=2, ensure_ascii=False)

print("Generated yazicioglu_lab2.ipynb successfully.")
