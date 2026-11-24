"""
Week 2 - White-box unit tests for helpers.py (BACKUP for Member 3)

Why helpers.py: it holds ALL the business rules (urgency, password and
username validation, the 7-day completion window). Every page and API
response depends on it, it has the most decision points per line, and it
is pure Python, so each branch can be driven directly.

Test IDs map to the control-flow analysis in White_Box_Analysis.md.
Run:  pytest _BACKUP_Members_2_3_4/02_White_Box_Coverage --cov=app --cov-branch --cov-report=term-missing
"""
from datetime import date, datetime

import pytest

from helpers import completed_in_last_n_days, compute_urgency, is_valid_password, is_valid_username

TODAY = date(2026, 11, 24)


# ---------------- compute_urgency  (V(G) = 5 -> 5 basis paths) -------------
@pytest.mark.parametrize("tc_id, due, expected", [
    ("TC-WB-001", None, "No due date"),          # P1: D2 true
    ("TC-WB-002", "", "No due date"),            # P1 (falsy string, same branch)
    ("TC-WB-003", "2026-11-23", "Overdue"),       # P2: D3 true (past)
    ("TC-WB-004", "2026-11-24", "Due Today"),     # P2': D3 true (today) -> spec says Due Today  [DEF-013]
    ("TC-WB-005", "2026-11-25", "Due Soon"),      # P3: D4 true, delta=1
    ("TC-WB-006", "2026-11-26", "Due Soon"),      # P3: D4 true, delta=2 (boundary)
    ("TC-WB-007", "2026-11-27", "Upcoming"),      # P4: D4 false, delta=3 (boundary)
])
def test_compute_urgency_branches(tc_id, due, expected):
    assert compute_urgency(due, today=TODAY) == expected


def test_TC_WB_008_compute_urgency_default_today_branch():
    """P5: D1 true - 'today' not supplied, falls back to date.today()."""
    assert compute_urgency("2999-01-01") == "Upcoming"


def test_TC_WB_009_compute_urgency_malformed_date_raises():
    """Data-flow: due_date_str is used by strptime with no guard. Documents the
    unhandled ValueError that becomes HTTP 500 in the API (DEF-009)."""
    with pytest.raises(ValueError):
        compute_urgency("2026-13-45", today=TODAY)


# ---------------- is_valid_password  (V(G) = 3) -----------------------------
@pytest.mark.parametrize("tc_id, pw, expected", [
    ("TC-WB-010", None, False),          # D1 true: not a str
    ("TC-WB-011", 12345678, False),      # D1 true: int
    ("TC-WB-012", "a" * 7, False),       # D2 false
    ("TC-WB-013", "a" * 8, True),        # D2 boundary: spec 'at least 8'  [DEF-012]
    ("TC-WB-014", "a" * 9, True),        # D2 true
])
def test_is_valid_password_branches(tc_id, pw, expected):
    assert is_valid_password(pw) is expected


# ---------------- is_valid_username  (V(G) = 4 + loop) ----------------------
@pytest.mark.parametrize("tc_id, name, expected", [
    ("TC-WB-015", 123, False),            # D1 true
    ("TC-WB-016", "ab", False),           # D2 true (too short)
    ("TC-WB-017", "a" * 21, False),       # D2 true (too long)
    ("TC-WB-018", "abc", True),           # D2 false, loop all true
    ("TC-WB-019", "a" * 20, True),        # upper boundary
    ("TC-WB-020", "ab_c9", True),         # loop: '_' branch of the OR
    ("TC-WB-021", "ab-c", False),         # loop: both OR operands false
    ("TC-WB-022", "", False),             # empty string: str but len 0
])
def test_is_valid_username_branches(tc_id, name, expected):
    assert is_valid_username(name) is expected


def test_TC_WB_023_username_accepts_non_ascii_letters():
    """Observation: str.isalnum() is Unicode-aware, so 'café' is accepted.
    Spec says 'letters' - ambiguous; recorded as an observation, not a defect."""
    assert is_valid_username("café") is True


# ---------------- completed_in_last_n_days  (V(G) = 5) ----------------------
NOW = datetime(2026, 11, 24, 12, 0, 0)


@pytest.mark.parametrize("tc_id, completed, expected", [
    ("TC-WB-024", None, False),                     # D1 true
    ("TC-WB-025", "2026-11-24 11:00:00", True),     # 1 hour ago
    ("TC-WB-026", "2026-11-18 12:00:00", True),     # 6 days ago
    ("TC-WB-027", "2026-11-17 12:00:01", True),     # just under 7 days
    ("TC-WB-028", "2026-11-17 12:00:00", True),     # exactly 7 days -> spec: inclusive  [DEF-015]
    ("TC-WB-029", "2026-11-16 12:00:00", False),    # 8 days
    ("TC-WB-030", "2026-11-25 12:00:00", False),    # future timestamp: total_seconds() > 0 false
])
def test_completed_in_last_n_days_branches(tc_id, completed, expected):
    assert completed_in_last_n_days(completed, n=7, now=NOW) is expected


def test_TC_WB_031_completed_default_now_branch():
    """D2 true - 'now' not supplied, defaults to datetime.now()."""
    assert completed_in_last_n_days("2000-01-01 00:00:00") is False
