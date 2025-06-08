import pytest
from goal_checker import GoalChecker
from models import UserData, UserToTag


def test_has_active_goal_true():
    """Test has_active_goal returns True for valid goal."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [5, "2025-12-31"],
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.has_active_goal(user_data) is True


def test_has_active_goal_false_empty():
    """Test has_active_goal returns False for empty goal."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [],
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.has_active_goal(user_data) is False


def test_has_active_goal_false_incomplete():
    """Test has_active_goal returns False for incomplete goal."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [5],  # Missing end date
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.has_active_goal(user_data) is False


def test_is_goal_expired_true():
    """Test is_goal_expired returns True for expired goal."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [5, "2020-01-01"],  # Expired date
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.is_goal_expired(user_data, "2025-01-01") is True


def test_is_goal_expired_false():
    """Test is_goal_expired returns False for active goal."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [5, "2025-12-31"],  # Future date
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.is_goal_expired(user_data, "2025-01-01") is False


def test_get_daily_goal():
    """Test get_daily_goal returns correct value."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [3, "2025-12-31"],
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.get_daily_goal(user_data) == 3


def test_get_daily_goal_no_goal():
    """Test get_daily_goal returns None for no goal."""
    user_data: UserData = {
        "lc_id": "test",
        "goal": [],
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 0,
        "points": 0,
        "weekly_points": 0,
    }
    assert GoalChecker.get_daily_goal(user_data) is None


def test_check_goal_achievement_true():
    """Test check_goal_achievement returns True when goal is met."""
    assert GoalChecker.check_goal_achievement(5, 3) is True
    assert GoalChecker.check_goal_achievement(3, 3) is True


def test_check_goal_achievement_false():
    """Test check_goal_achievement returns False when goal is not met."""
    assert GoalChecker.check_goal_achievement(2, 3) is False
    assert GoalChecker.check_goal_achievement(0, 1) is False


def test_get_users_to_tag():
    """Test get_users_to_tag returns correct users."""
    db = {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2025-12-31"],  # Active goal, needs 3 points
            "easySolved": 0,
            "mediumSolved": 0,
            "hardSolved": 0,
            "points": 0,
            "weekly_points": 0,
        },
        "user2": {
            "lc_id": "user2_lc",
            "goal": [2, "2025-12-31"],  # Active goal, needs 2 points
            "easySolved": 0,
            "mediumSolved": 0,
            "hardSolved": 0,
            "points": 0,
            "weekly_points": 0,
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

    points_gained_by_user = {
        "user1": 1,  # Didn't meet goal (needs 3, got 1)
        "user2": 3,  # Met goal (needs 2, got 3)
        "user3": 0,  # No goal
    }

    users_to_tag = GoalChecker.get_users_to_tag(db, points_gained_by_user, "2025-01-01")

    assert len(users_to_tag) == 1
    assert users_to_tag[0].username == "user1"
    assert users_to_tag[0].daily_goal == 3


def test_get_users_to_tag_expired_goal():
    """Test get_users_to_tag skips users with expired goals."""
    db = {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2020-01-01"],  # Expired goal
            "easySolved": 0,
            "mediumSolved": 0,
            "hardSolved": 0,
            "points": 0,
            "weekly_points": 0,
        }
    }

    points_gained_by_user = {"user1": 1}

    users_to_tag = GoalChecker.get_users_to_tag(db, points_gained_by_user, "2025-01-01")

    assert len(users_to_tag) == 0
