"""
Consensus and Decentralized Governance Simulation Module for Lab 2
Course: Blockchain and its Application (Zima 2026/2027)
Instructor: Vishnu Suresh
Author: Kaan Yazıcıoğlu
"""

from typing import Any, Dict, List, Optional, Set, Tuple


def validate_proposal(
    proposal: Dict[str, Any],
    validators: List[str],
    required_fields: Optional[Set[str]] = None,
) -> Tuple[bool, str]:
    """Validates credential proposal against schema and authorized issuer list."""
    if required_fields is None:
        required_fields = {"student", "credential", "issuer"}

    missing = required_fields - set(proposal.keys())
    if missing:
        return False, f"Missing fields: {sorted(missing)}"

    if proposal.get("issuer") not in validators:
        return False, "Issuer is not a consortium member"

    return True, "Proposal follows the rules"


def quorum_result(
    votes: Dict[str, Optional[bool]],
    threshold: int = 4,
) -> Tuple[bool, int, int]:
    """
    Computes quorum outcome given a dictionary of validator votes.
    Returns: (is_approved, approval_count, responding_count)
    """
    approvals = sum(vote is True for vote in votes.values())
    responding = sum(vote is not None for vote in votes.values())
    return approvals >= threshold, approvals, responding


def has_quorum(voter_set: Set[str], threshold: int) -> bool:
    """Checks if a given set of voters meets or exceeds the quorum threshold."""
    return len(set(voter_set)) >= threshold


def simple_majority(votes: Dict[str, bool]) -> bool:
    """Calculates whether True votes exceed strict majority (> 50%)."""
    if not votes:
        return False
    approvals = sum(1 for v in votes.values() if v is True)
    return approvals > (len(votes) / 2)


def minimum_coalition(
    weights: Dict[str, float],
    threshold: float,
) -> Tuple[List[str], float]:
    """
    Calculates the minimum coalition (Nakamoto-style metric) needed to reach or exceed a voting threshold.
    Returns: (coalition_members, total_weight_accumulated)
    """
    ordered = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    coalition: List[str] = []
    total: float = 0.0

    for validator, weight in ordered:
        coalition.append(validator)
        total += weight
        if total >= threshold:
            return coalition, total

    return coalition, total
