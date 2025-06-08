import pytest
from points_calculator import PointsCalculator
from models import UserStats


def test_calculate_points():
    """Test points calculation."""
    stats: UserStats = {
        "solvedProblem": 10,
        "easySolved": 5,
        "mediumSolved": 3,
        "hardSolved": 2,
        "totalSubmissionNum": [],
        "acSubmissionNum": [],
    }

    points = PointsCalculator.calculate_points(stats)
    # 5*1 + 3*2 + 2*3 = 5 + 6 + 6 = 17
    assert points == 17


def test_calculate_points_all_easy():
    """Test points calculation with only easy problems."""
    stats: UserStats = {
        "solvedProblem": 10,
        "easySolved": 10,
        "mediumSolved": 0,
        "hardSolved": 0,
        "totalSubmissionNum": [],
        "acSubmissionNum": [],
    }

    points = PointsCalculator.calculate_points(stats)
    assert points == 10


def test_calculate_points_all_hard():
    """Test points calculation with only hard problems."""
    stats: UserStats = {
        "solvedProblem": 5,
        "easySolved": 0,
        "mediumSolved": 0,
        "hardSolved": 5,
        "totalSubmissionNum": [],
        "acSubmissionNum": [],
    }

    points = PointsCalculator.calculate_points(stats)
    assert points == 15


def test_calculate_points_gained_positive():
    """Test points gained calculation with positive gain."""
    gained = PointsCalculator.calculate_points_gained(20, 15)
    assert gained == 5


def test_calculate_points_gained_zero():
    """Test points gained calculation with no change."""
    gained = PointsCalculator.calculate_points_gained(15, 15)
    assert gained == 0


def test_calculate_points_gained_negative():
    """Test points gained calculation handles negative values."""
    gained = PointsCalculator.calculate_points_gained(10, 15)
    assert gained == 0  # Should not be negative
