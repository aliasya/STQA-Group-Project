from datetime import date, datetime, timedelta
from helpers import is_valid_password, is_valid_username, compute_urgency, completed_in_last_n_days


def test_valid_password():
    assert is_valid_password("Password123") is True


def test_password_exactly_8_characters():
    assert is_valid_password("Pass1234") is True


def test_password_less_than_8_characters():
    assert is_valid_password("Pass123") is False


def test_valid_username():
    assert is_valid_username("user_123") is True


def test_username_minimum_boundary():
    assert is_valid_username("abc") is True


def test_username_maximum_boundary():
    assert is_valid_username("a" * 20) is True


def test_username_too_short():
    assert is_valid_username("ab") is False


def test_username_too_long():
    assert is_valid_username("a" * 21) is False


def test_username_invalid_characters():
    assert is_valid_username("user@123") is False


def test_urgency_no_due_date():
    assert compute_urgency(None, date(2026, 11, 14)) == "No due date"


def test_urgency_overdue():
    assert compute_urgency("2026-11-13", date(2026, 11, 14)) == "Overdue"


def test_urgency_due_today():
    assert compute_urgency("2026-11-14", date(2026, 11, 14)) == "Due Today"


def test_urgency_due_soon():
    assert compute_urgency("2026-11-15", date(2026, 11, 14)) == "Due Soon"


def test_urgency_upcoming():
    assert compute_urgency("2026-11-17", date(2026, 11, 14)) == "Upcoming"


def test_completed_within_7_days():
    now = datetime(2026, 11, 14, 12, 0, 0)
    result = completed_in_last_n_days("2026-11-11 12:00:00", 7, now)
    assert result is True


def test_completed_exactly_7_days_ago():
    now = datetime(2026, 11, 14, 12, 0, 0)
    result = completed_in_last_n_days("2026-11-07 12:00:00", 7, now)
    assert result is True


def test_completed_more_than_7_days_ago():
    now = datetime(2026, 11, 14, 12, 0, 0)
    result = completed_in_last_n_days("2026-11-06 12:00:00", 7, now)
    assert result is False


def test_task_not_completed():
    now = datetime(2026, 11, 14, 12, 0, 0)
    result = completed_in_last_n_days(None, 7, now)
    assert result is False


def test_completed_in_future():
    now = datetime(2026, 11, 14, 12, 0, 0)
    result = completed_in_last_n_days("2026-11-15 12:00:00", 7, now)
    assert result is False


def test_urgency_default_today():
    tomorrow = date.today() + timedelta(days=1)
    result = compute_urgency(tomorrow.isoformat())
    assert result == "Due Soon"


def test_password_invalid_data_type():
    assert is_valid_password(None) is False


def test_username_invalid_data_type():
    assert is_valid_username(None) is False


def test_completed_default_now():
    now = datetime.now()
    completed_at = now - timedelta(days=1)
    result = completed_in_last_n_days(completed_at.strftime("%Y-%m-%d %H:%M:%S"), 7)
    assert result is True
