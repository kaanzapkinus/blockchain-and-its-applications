# Blockchain and its Application

**Course:** Blockchain and its Application  
**Instructor:** Vishnu Suresh  
**Group / Semester:** SD_S / Zima 2026/2027  
**Student:** Kaan Yazıcıoğlu  
**Repository:** [kaanzapkinus/blockchain-and-its-applications](https://github.com/kaanzapkinus/blockchain-and-its-applications)

---

## 📌 Repository Overview

This repository contains the laboratory implementations, experiments, and architectural design proposals for the course **Blockchain and its Application**.

### 🧪 Labs Included:
1. [**Lab 1: Building and Testing a Miniature Blockchain**](yazicioglu_lab1.ipynb)
   - Cryptographic hashing (SHA-256) & avalanche effect
   - Linked blocks & tamper detection
   - Proof of Work (PoW) mining benchmarks
   - Fork choice & longest chain rule
   - Two-layer validation (Block Integrity vs. Transaction Validity)
2. [**Lab 2: Simulating Decentralized Agreement and Control**](yazicioglu_lab2.ipynb)
   - Consortium trust model & quorum approval (4-of-5)
   - Crash faults vs. Byzantine dishonest validator faults
   - Network partitions & CAP/FLM trade-offs (Safety vs. Liveness)
   - Sybil resistance (Open identity attack vs. Permissioned whitelist)
   - Effective control & minimum coalition (Equal vs. Concentrated vs. Extreme)
   - Decentralization design proposal for shared academic credentialing

---

## 📂 Repository Structure

```text
.
├── README.md               # Course & project documentation
├── requirements.txt        # Jupyter environment requirements
├── yazicioglu_lab1.ipynb   # Lab 1 Jupyter Notebook
├── yazicioglu_lab2.ipynb   # Lab 2 Jupyter Notebook
├── build_notebook.py       # Automation script for Lab 1 notebook
├── build_notebook_lab2.py  # Automation script for Lab 2 notebook
└── src/
    ├── blockchain.py       # Core blockchain engine (Lab 1)
    └── consensus.py        # Consortium consensus & quorum module (Lab 2)
```

---

## 🚀 Getting Started

### Prerequisites & Setup
A local Python virtual environment is configured with Jupyter Notebook support:

```bash
# Clone the repository
git clone https://github.com/kaanzapkinus/blockchain-and-its-applications.git
cd blockchain-and-its-applications

# Activate virtual environment
source .venv/bin/activate

# Launch Jupyter Notebook
jupyter notebook
```

---

## 📊 Lab 1 Highlight: Proof of Work Benchmark

| Difficulty | Required Prefix | Attempts | Execution Time (s) | Hashrate (H/s) | Resulting Block Hash |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **2** | `00` | 388 | ~0.0010s | ~380,000 | `00f1bf0d23b2a92227...` |
| **3** | `000` | 5,107 | ~0.0140s | ~365,000 | `0003ea59b1979b9db0...` |
| **4** | `0000` | 105,827 | ~0.2880s | ~367,000 | `0000e7d44076c28523...` |

---

## 🛡️ Lab 2 Highlight: Consensus & Fault Tolerance Matrix

| Scenario / Experiment | Threshold | Outcome | System State |
| :--- | :---: | :---: | :--- |
| **Normal Quorum** | 4 / 5 | Approved (5/5) | Full consensus reached |
| **1 Crash Fault** | 4 / 5 | Approved (4/4) | Resilient to node dropouts |
| **1 Byzantine Traitor** | 4 / 5 | Approved (4/5) | Dishonest vote rejected / bypassed |
| **3-2 Network Partition** | 4 / 5 | Paused (0/5) | **Safety preserved**, Liveness halts |
| **Lowered Threshold + Equivocation** | 3 / 5 | Conflicting (3/5 each) | **Safety violated** (Split-brain consensus) |
| **Open Voting (Sybil Attack)** | > 50% | Attacker wins (20/25) | Trivial capture by fake identities |
| **Whitelisted Consortium** | > 50% | Honest wins (5/5) | Sybil attack completely neutralized |
| **Extreme Voting Weight (70%)** | 67% | Coalition size = 1 (`['A']`) | Validator count deceptive; centralized |

---

## 📜 License
Educational work prepared for *Blockchain and its Application* (Zima 2026/2027).
