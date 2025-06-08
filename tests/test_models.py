import pytest
from models import PROBLEM_SCALE, UserToTag, LeaderboardEntry


def test_problem_scale():
    """Test that problem scale has correct values."""
    assert PROBLEM_SCALE["easy"] == 1
    assert PROBLEM_SCALE["medium"] == 2
    assert PROBLEM_SCALE["hard"] == 3


def test_user_to_tag():
    """Test UserToTag dataclass."""
    user = UserToTag(username="testuser", daily_goal=5)
    assert user.username == "testuser"
    assert user.daily_goal == 5


def test_leaderboard_entry():
    """Test LeaderboardEntry dataclass."""
    entry = LeaderboardEntry(username="testuser", points=10)
    assert entry.username == "testuser"
    assert entry.points == 10
