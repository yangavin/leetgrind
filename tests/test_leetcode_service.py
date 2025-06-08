import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import json
import os

from leetcode_service import LeetCodeService
from models import UserStats, UserToTag, LeaderboardEntry


@pytest.fixture
def temp_db_file():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def sample_db():
    """Sample database for testing."""
    return {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2025-12-31"],  # Needs 3 points daily
            "easySolved": 5,
            "mediumSolved": 3,
            "hardSolved": 1,
            "points": 14,
            "weekly_points": 10,
        },
        "user2": {
            "lc_id": "user2_lc",
            "goal": [2, "2025-12-31"],  # Needs 2 points daily
            "easySolved": 10,
            "mediumSolved": 5,
            "hardSolved": 2,
            "points": 26,
            "weekly_points": 5,
        },
        "user3": {
            "lc_id": "user3_lc",
            "goal": [],  # No goal
            "easySolved": 0,
            "mediumSolved": 0,
            "hardSolved": 0,
            "points": 0,
            "weekly_points": 0,
        },
    }


@pytest.fixture
def sample_api_responses():
    """Sample API responses for testing."""
    return {
        "user1_lc": {
            "solvedProblem": 10,
            "easySolved": 6,  # Gained 1 easy (1 point)
            "mediumSolved": 3,  # No change
            "hardSolved": 1,  # No change
            "totalSubmissionNum": [],
            "acSubmissionNum": [],
        },
        "user2_lc": {
            "solvedProblem": 20,
            "easySolved": 10,  # No change
            "mediumSolved": 6,  # Gained 1 medium (2 points)
            "hardSolved": 2,  # No change
            "totalSubmissionNum": [],
            "acSubmissionNum": [],
        },
        "user3_lc": {
            "solvedProblem": 5,
            "easySolved": 2,  # Gained 2 easy (2 points)
            "mediumSolved": 1,  # Gained 1 medium (2 points)
            "hardSolved": 0,  # No change
            "totalSubmissionNum": [],
            "acSubmissionNum": [],
        },
    }


@patch("leetcode_service.datetime")
def test_check_and_update_progress_regular_day(
    mock_datetime, temp_db_file, sample_db, sample_api_responses
):
    """Test check_and_update_progress on a regular day (not Monday)."""
    # Setup
    with open(temp_db_file, "w") as f:
        json.dump(sample_db, f)

    # Mock datetime to return Tuesday (weekday = 1)
    mock_now = Mock()
    mock_now.weekday.return_value = 1  # Tuesday
    mock_now.strftime.return_value = "2025-01-01"
    mock_datetime.now.return_value = mock_now

    service = LeetCodeService("https://api.example.com", temp_db_file)

    # Mock API responses
    def mock_get_user_stats(lc_id):
        return sample_api_responses.get(lc_id)

    service.leetcode_api.get_user_stats = mock_get_user_stats

    # Test with update_db=True
    users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
        update_db=True
    )

    # Check results
    assert is_monday is False
    assert leaderboard == []  # No leaderboard on non-Monday

    # user1 gained 1 point, needs 3 -> should be tagged
    # user2 gained 2 points, needs 2 -> should NOT be tagged
    # user3 has no goal -> should NOT be tagged
    assert len(users_to_tag) == 1
    assert users_to_tag[0].username == "user1"
    assert users_to_tag[0].daily_goal == 3

    # Check database was updated
    with open(temp_db_file, "r") as f:
        updated_db = json.load(f)

    # user1: 6*1 + 3*2 + 1*3 = 15 points (gained 1 from 14)
    assert updated_db["user1"]["points"] == 15
    assert updated_db["user1"]["weekly_points"] == 11  # 10 + 1

    # user2: 10*1 + 6*2 + 2*3 = 28 points (gained 2 from 26)
    assert updated_db["user2"]["points"] == 28
    assert updated_db["user2"]["weekly_points"] == 7  # 5 + 2


@patch("leetcode_service.datetime")
def test_check_and_update_progress_monday(
    mock_datetime, temp_db_file, sample_db, sample_api_responses
):
    """Test check_and_update_progress on Monday."""
    # Setup
    with open(temp_db_file, "w") as f:
        json.dump(sample_db, f)

    # Mock datetime to return Monday (weekday = 0)
    mock_now = Mock()
    mock_now.weekday.return_value = 0  # Monday
    mock_now.strftime.return_value = "2025-01-01"
    mock_datetime.now.return_value = mock_now

    service = LeetCodeService("https://api.example.com", temp_db_file)

    # Mock API responses
    def mock_get_user_stats(lc_id):
        return sample_api_responses.get(lc_id)

    service.leetcode_api.get_user_stats = mock_get_user_stats

    # Test with update_db=True
    users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
        update_db=True
    )

    # Check results
    assert is_monday is True
    assert len(leaderboard) == 3  # Should have leaderboard

    # Leaderboard should be sorted by weekly points descending
    assert leaderboard[0].username == "user1"
    assert leaderboard[0].points == 10
    assert leaderboard[1].username == "user2"
    assert leaderboard[1].points == 5
    assert leaderboard[2].username == "user3"
    assert leaderboard[2].points == 0

    # Check database was updated and weekly points reset
    with open(temp_db_file, "r") as f:
        updated_db = json.load(f)

    # Weekly points should be reset to 0 then updated with gained points
    # user1 gained 1 point, so weekly_points = 0 + 1 = 1
    # user2 gained 2 points, so weekly_points = 0 + 2 = 2
    # user3 gained 4 points, so weekly_points = 0 + 4 = 4
    assert updated_db["user1"]["weekly_points"] == 1
    assert updated_db["user2"]["weekly_points"] == 2
    assert updated_db["user3"]["weekly_points"] == 4


def test_check_and_update_progress_no_update(
    temp_db_file, sample_db, sample_api_responses
):
    """Test check_and_update_progress with update_db=False."""
    # Setup
    with open(temp_db_file, "w") as f:
        json.dump(sample_db, f)

    service = LeetCodeService("https://api.example.com", temp_db_file)

    # Mock API responses
    def mock_get_user_stats(lc_id):
        return sample_api_responses.get(lc_id)

    service.leetcode_api.get_user_stats = mock_get_user_stats

    # Test with update_db=False
    users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
        update_db=False
    )

    # Check results are still calculated correctly
    assert len(users_to_tag) == 1
    assert users_to_tag[0].username == "user1"

    # Check database was NOT updated
    with open(temp_db_file, "r") as f:
        updated_db = json.load(f)

    # Should be exactly the same as original
    assert updated_db == sample_db


def test_check_and_update_progress_api_failure(temp_db_file, sample_db):
    """Test check_and_update_progress with API failures."""
    # Setup
    with open(temp_db_file, "w") as f:
        json.dump(sample_db, f)

    service = LeetCodeService("https://api.example.com", temp_db_file)

    # Mock API to return None (failure)
    service.leetcode_api.get_user_stats = Mock(return_value=None)

    # Test
    users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
        update_db=True
    )

    # Should tag users who have goals but gained 0 points due to API failure
    assert len(users_to_tag) == 2  # user1 and user2 have goals, user3 doesn't

    # Database should remain unchanged except for weekly_points initialization
    with open(temp_db_file, "r") as f:
        updated_db = json.load(f)

    # Points should remain the same
    assert updated_db["user1"]["points"] == 14
    assert updated_db["user2"]["points"] == 26


def test_check_and_update_progress_expired_goals(temp_db_file, sample_api_responses):
    """Test check_and_update_progress with expired goals."""
    # Setup database with expired goals
    db_with_expired_goals = {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2020-01-01"],  # Expired goal
            "easySolved": 5,
            "mediumSolved": 3,
            "hardSolved": 1,
            "points": 14,
            "weekly_points": 10,
        }
    }

    with open(temp_db_file, "w") as f:
        json.dump(db_with_expired_goals, f)

    service = LeetCodeService("https://api.example.com", temp_db_file)

    # Mock API responses
    def mock_get_user_stats(lc_id):
        return sample_api_responses.get(lc_id)

    service.leetcode_api.get_user_stats = mock_get_user_stats

    # Test
    users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
        update_db=True
    )

    # Should not tag user with expired goal
    assert len(users_to_tag) == 0

    # Check that expired goal was cleared
    with open(temp_db_file, "r") as f:
        updated_db = json.load(f)

    assert updated_db["user1"]["goal"] == []
