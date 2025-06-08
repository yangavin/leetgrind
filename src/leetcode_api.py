import requests
from typing import Optional

from .models import UserStats


class LeetCodeAPI:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_user_stats(self, lc_id: str) -> Optional[UserStats]:
        """Fetch user statistics from LeetCode API."""
        try:
            response = requests.get(f"{self.api_url}/{lc_id}/solved")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching stats for {lc_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching stats for {lc_id}: {e}")
            return None
