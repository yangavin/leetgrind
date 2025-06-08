import pytest
import tempfile
import json
import os
from database import DatabaseManager
from models import UserData


@pytest.fixture
def temp_db_file():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_db():
    """Sample database data for testing."""
    return {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2025-12-31"],
            "easySolved": 5,
            "mediumSolved": 3,
            "hardSolved": 1,
            "points": 14,
            "weekly_points": 5,
        },
        "user2": {
            "lc_id": "user2_lc",
            "goal": [],
            "easySolved": 10,
            "mediumSolved": 5,
            "hardSolved": 2,
            "points": 26,
            "weekly_points": 10,
        },
    }


def test_get_db_empty_file(temp_db_file):
    """Test get_db returns empty dict for non-existent file."""
    os.unlink(temp_db_file)  # Remove the temp file
    db_manager = DatabaseManager(temp_db_file)
    result = db_manager.get_db()
    assert result == {}


def test_get_db_valid_file(temp_db_file, sample_db):
    """Test get_db returns correct data from valid file."""
    with open(temp_db_file, "w") as f:
        json.dump(sample_db, f)

    db_manager = DatabaseManager(temp_db_file)
    result = db_manager.get_db()
    assert result == sample_db


def test_get_db_invalid_json(temp_db_file):
    """Test get_db raises error for invalid JSON."""
    with open(temp_db_file, "w") as f:
        f.write("invalid json")

    db_manager = DatabaseManager(temp_db_file)
    with pytest.raises(ValueError, match="Invalid JSON"):
        db_manager.get_db()


def test_save_db(temp_db_file, sample_db):
    """Test save_db writes data correctly."""
    db_manager = DatabaseManager(temp_db_file)
    db_manager.save_db(sample_db)

    with open(temp_db_file, "r") as f:
        result = json.load(f)
    assert result == sample_db


def test_initialize_weekly_points(sample_db):
    """Test initialize_weekly_points adds missing weekly_points."""
    # Remove weekly_points from user1
    test_db = sample_db.copy()
    del test_db["user1"]["weekly_points"]

    db_manager = DatabaseManager()
    result = db_manager.initialize_weekly_points(test_db)

    assert result["user1"]["weekly_points"] == 0
    assert result["user2"]["weekly_points"] == 10  # Should remain unchanged


def test_reset_weekly_points(sample_db):
    """Test reset_weekly_points resets all weekly points to 0."""
    db_manager = DatabaseManager()
    result = db_manager.reset_weekly_points(sample_db)

    assert result["user1"]["weekly_points"] == 0
    assert result["user2"]["weekly_points"] == 0


def test_update_user_stats(sample_db):
    """Test update_user_stats updates user statistics correctly."""
    db_manager = DatabaseManager()
    result = db_manager.update_user_stats(sample_db, "user1", 6, 4, 2, 20, 6)

    assert result["user1"]["easySolved"] == 6
    assert result["user1"]["mediumSolved"] == 4
    assert result["user1"]["hardSolved"] == 2
    assert result["user1"]["points"] == 20
    assert result["user1"]["weekly_points"] == 11  # 5 + 6


def test_update_user_stats_nonexistent_user(sample_db):
    """Test update_user_stats with non-existent user."""
    db_manager = DatabaseManager()
    result = db_manager.update_user_stats(sample_db, "nonexistent", 1, 1, 1, 5, 2)

    # Should return original database unchanged
    assert result == sample_db


def test_clear_expired_goals():
    """Test clear_expired_goals removes expired goals."""
    db = {
        "user1": {
            "lc_id": "user1_lc",
            "goal": [3, "2020-01-01"],  # Expired
            "easySolved": 0,
            "mediumSolved": 0,
            "hardSolved": 0,
            "points": 0,
            "weekly_points": 0,
        },
        "user2": {
            "lc_id": "user2_lc",
            "goal": [3, "2025-12-31"],  # Not expired
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

    db_manager = DatabaseManager()
    result = db_manager.clear_expired_goals(db, "2025-01-01")

    assert result["user1"]["goal"] == []  # Should be cleared
    assert result["user2"]["goal"] == [3, "2025-12-31"]  # Should remain
    assert result["user3"]["goal"] == []  # Should remain empty
