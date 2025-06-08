import json
import os
from typing import Dict
from copy import deepcopy

from .models import UserData


class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "db.json")
        self.db_path = db_path

    def get_db(self) -> Dict[str, UserData]:
        """Load the database from JSON file."""
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in database file: {self.db_path}")

    def save_db(self, db: Dict[str, UserData]) -> None:
        """Save the database to JSON file."""
        with open(self.db_path, "w") as f:
            json.dump(db, f, indent=4)

    def initialize_weekly_points(self, db: Dict[str, UserData]) -> Dict[str, UserData]:
        """Initialize weekly_points for users who don't have it."""
        updated_db = deepcopy(db)
        for username in updated_db:
            if "weekly_points" not in updated_db[username]:
                updated_db[username]["weekly_points"] = 0
        return updated_db

    def reset_weekly_points(self, db: Dict[str, UserData]) -> Dict[str, UserData]:
        """Reset weekly points for all users."""
        updated_db = deepcopy(db)
        for username in updated_db:
            updated_db[username]["weekly_points"] = 0
        return updated_db

    def update_user_stats(
        self,
        db: Dict[str, UserData],
        username: str,
        easy_solved: int,
        medium_solved: int,
        hard_solved: int,
        points: int,
        points_gained: int,
    ) -> Dict[str, UserData]:
        """Update user's stats and weekly points."""
        updated_db = deepcopy(db)
        if username in updated_db:
            updated_db[username]["easySolved"] = easy_solved
            updated_db[username]["mediumSolved"] = medium_solved
            updated_db[username]["hardSolved"] = hard_solved
            updated_db[username]["points"] = points
            updated_db[username]["weekly_points"] += points_gained
        return updated_db

    def clear_expired_goals(
        self, db: Dict[str, UserData], current_date: str
    ) -> Dict[str, UserData]:
        """Clear goals that have expired."""
        updated_db = deepcopy(db)
        for username, user_data in updated_db.items():
            if (
                user_data.get("goal")
                and len(user_data["goal"]) >= 2
                and current_date > user_data["goal"][1]
            ):
                updated_db[username]["goal"] = []
        return updated_db
