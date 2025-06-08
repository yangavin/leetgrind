import pytest
from unittest.mock import Mock
from leaderboard import LeaderboardManager
from models import UserData, LeaderboardEntry


@pytest.fixture
def sample_db():
    """Sample database for testing."""
    return {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2025-12-31"],
            "easySolved": 5,
            "mediumSolved": 3,
            "hardSolved": 1,
            "points": 14,
            "weekly_points": 15,
        },
        "user2": {
            "lc_id": "user2_lc",
            "goal": [],
            "easySolved": 10,
            "mediumSolved": 5,
            "hardSolved": 2,
            "points": 26,
            "weekly_points": 5,
        },
        "user3": {
            "lc_id": "user3_lc",
            "goal": [],
            "easySolved": 0,
            "mediumSolved": 0,
            "hardSolved": 0,
            "points": 0,
            "weekly_points": 0,
        },
    }


def test_get_weekly_leaderboard(sample_db):
    """Test get_weekly_leaderboard returns sorted leaderboard."""
    leaderboard = LeaderboardManager.get_weekly_leaderboard(sample_db)

    assert len(leaderboard) == 3
    # Should be sorted by points descending
    assert leaderboard[0].username == "user1"
    assert leaderboard[0].points == 15
    assert leaderboard[1].username == "user2"
    assert leaderboard[1].points == 5
    assert leaderboard[2].username == "user3"
    assert leaderboard[2].points == 0


def test_get_weekly_leaderboard_empty():
    """Test get_weekly_leaderboard with empty database."""
    leaderboard = LeaderboardManager.get_weekly_leaderboard({})
    assert leaderboard == []


def test_format_leaderboard_message_empty():
    """Test format_leaderboard_message with empty leaderboard."""
    message = LeaderboardManager.format_leaderboard_message([], None)
    assert message == "No points scored this week!"


def test_format_leaderboard_message_with_points():
    """Test format_leaderboard_message with users having points."""
    # Mock guild and members
    mock_guild = Mock()
    mock_member1 = Mock()
    mock_member1.id = 123
    mock_member2 = Mock()
    mock_member2.id = 456

    # Mock discord.utils.get to return our mock members
    import discord

    original_get = discord.utils.get

    def mock_get(members, name):
        if name == "user1":
            return mock_member1
        elif name == "user2":
            return mock_member2
        return None

    discord.utils.get = mock_get

    try:
        leaderboard = [
            LeaderboardEntry(username="user1", points=10),
            LeaderboardEntry(username="user2", points=5),
            LeaderboardEntry(username="user3", points=0),
        ]

        message = LeaderboardManager.format_leaderboard_message(leaderboard, mock_guild)

        assert "# 🏆 Leaderboard 🏆" in message
        assert "1. <@123> - `10 pts`" in message
        assert "2. <@456> - `5 pts`" in message
        assert "0 points and will forever be unemployed:" in message
        assert "user3" in message

    finally:
        # Restore original function
        discord.utils.get = original_get


def test_format_leaderboard_message_all_zero_points():
    """Test format_leaderboard_message with all users having 0 points."""
    # Mock guild and members
    mock_guild = Mock()
    mock_member1 = Mock()
    mock_member1.id = 123

    import discord

    original_get = discord.utils.get

    def mock_get(members, name):
        if name == "user1":
            return mock_member1
        return None

    discord.utils.get = mock_get

    try:
        leaderboard = [
            LeaderboardEntry(username="user1", points=0),
            LeaderboardEntry(username="user2", points=0),
        ]

        message = LeaderboardManager.format_leaderboard_message(leaderboard, mock_guild)

        assert "# 🏆 Leaderboard 🏆" in message
        assert "0 points and will forever be unemployed:" in message
        assert "<@123>" in message
        assert "user2" in message  # No member found, so uses username

    finally:
        discord.utils.get = original_get
