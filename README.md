# Blockchain and its Application

**Course:** Blockchain and its Application  
**Instructor:** Vishnu Suresh  
**Group / Semester:** SD_S / Zima 2026/2027  
**Student:** Kaan Yazıcıoğlu  
**Laboratory Assignment:** Lab 1 – Building and Testing a Miniature Blockchain  

---

## 📌 Overview

This repository contains the practical implementation and experimentation for **Lab 1: Building and Testing a Miniature Blockchain**. 

The goal of this laboratory is to demystify blockchain mechanics by constructing a transparent, lightweight educational blockchain engine entirely from scratch using standard Python 3.

### Key Objectives & Covered Topics:
1. **Cryptographic Hashes & Determinism:** Demonstrating SHA-256 properties, input sensitivity, and the avalanche effect.
2. **Linked Blocks & Chain Architecture:** Constructing cryptographic linkages (`previous_hash`) and calculating block hashes from serialized state.
3. **Tamper Detection & Verification:** Implementing dual-condition chain validation to detect data tampering and broken links.
4. **Simplified Proof of Work (PoW):** Implementing trial-and-error nonce mining against difficulty targets, profiling mining attempts and execution time.
5. **Competing Histories & Fork Choice:** Simulating forks with conflicting transaction histories and applying the longest chain consensus rule.
6. **Advanced Transaction Validation & Architecture:** Decoupling **Block Integrity** (cryptographic consensus) from **Transaction Validity** (semantic business rules) using a two-layer validation model.

---

## 📂 Repository Structure

```text
.
├── README.md               # Course & project documentation
├── yazicioglu_lab1.ipynb   # Main Jupyter Notebook containing all experiments, code, and explanations
└── src/
    └── blockchain.py       # Modularized core blockchain engine & validation logic
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Jupyter Notebook / JupyterLab or VS Code with Jupyter extension
- Only standard library modules are required (`hashlib`, `json`, `copy`, `time`, `re`). No heavy external dependencies.

### Running the Notebook
```bash
# Clone the repository
git clone https://github.com/kaanzapkinus/blockchain-and-its-applications.git
cd blockchain-and-its-applications

# Launch Jupyter Notebook
jupyter notebook yazicioglu_lab1.ipynb
```

---

## 📊 Proof of Work Difficulty Benchmark (Part 4)

| Difficulty | Required Prefix | Attempts | Execution Time (s) | Hashrate (H/s) | Resulting Block Hash |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **2** | `00` | 388 | ~0.0010s | ~380,000 | `00f1bf0d23b2a92227...` |
| **3** | `000` | 5,107 | ~0.0140s | ~365,000 | `0003ea59b1979b9db0...` |
| **4** | `0000` | 105,827 | ~0.2880s | ~367,000 | `0000e7d44076c28523...` |

> *Note:* Each additional hexadecimal zero increases the expected search space by $16\times$ ($16^d$). Because hashing is a memoryless Poisson process, empirical trial counts naturally deviate around the theoretical expectation while verification remains instantaneous ($\mathcal{O}(1)$).

---

## 💡 Conceptual Highlight: Block Integrity vs. Transaction Validity

A critical insight highlighted in this project is the conceptual difference between **Block Integrity** and **Transaction Validity**:

> 📦 **The Wax-Sealed Envelope Analogy:**  
> - **Block Integrity:** Verifies that the envelope has not been opened or tampered with in transit (valid hash, valid previous hash, and sufficient proof of work).
> - **Transaction Validity:** Verifies whether the check *inside* the envelope is economically and semantically valid (e.g., account balance, non-negative amounts, distinct sender and receiver).
> 
> A block can possess flawless cryptographic integrity and satisfy all proof-of-work requirements while still containing an invalid or fraudulent transaction if nodes do not enforce semantic validation rules.

---

## 📜 License
This repository is created for educational purposes under the course *Blockchain and its Application* (Zima 2026/2027).
