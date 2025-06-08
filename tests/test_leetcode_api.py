import pytest
from unittest.mock import Mock, patch
import requests
from leetcode_api import LeetCodeAPI
from models import UserStats


@pytest.fixture
def api():
    """Create LeetCodeAPI instance for testing."""
    return LeetCodeAPI("https://api.example.com")


@pytest.fixture
def sample_user_stats():
    """Sample user stats from API."""
    return {
        "solvedProblem": 10,
        "easySolved": 5,
        "mediumSolved": 3,
        "hardSolved": 2,
        "totalSubmissionNum": [],
        "acSubmissionNum": [],
    }


@patch("leetcode_api.requests.get")
def test_get_user_stats_success(mock_get, api, sample_user_stats):
    """Test successful API call."""
    mock_response = Mock()
    mock_response.json.return_value = sample_user_stats
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = api.get_user_stats("testuser")

    assert result == sample_user_stats
    mock_get.assert_called_once_with("https://api.example.com/testuser/solved")


@patch("leetcode_api.requests.get")
def test_get_user_stats_http_error(mock_get, api):
    """Test API call with HTTP error."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    result = api.get_user_stats("nonexistent")

    assert result is None
    mock_get.assert_called_once_with("https://api.example.com/nonexistent/solved")


@patch("leetcode_api.requests.get")
def test_get_user_stats_connection_error(mock_get, api):
    """Test API call with connection error."""
    mock_get.side_effect = requests.ConnectionError("Connection failed")

    result = api.get_user_stats("testuser")

    assert result is None
    mock_get.assert_called_once_with("https://api.example.com/testuser/solved")


@patch("leetcode_api.requests.get")
def test_get_user_stats_json_decode_error(mock_get, api):
    """Test API call with JSON decode error."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    result = api.get_user_stats("testuser")

    assert result is None
    mock_get.assert_called_once_with("https://api.example.com/testuser/solved")
