from datetime import datetime
from typing import Dict, List, Tuple

from .database import DatabaseManager
from .leetcode_api import LeetCodeAPI
from .points_calculator import PointsCalculator
from .goal_checker import GoalChecker
from .leaderboard import LeaderboardManager
from .models import UserToTag, LeaderboardEntry, UserData


class LeetCodeService:
    def __init__(self, api_url: str, db_path: str = None):
        self.db_manager = DatabaseManager(db_path)
        self.leetcode_api = LeetCodeAPI(api_url)
        self.points_calculator = PointsCalculator()
        self.goal_checker = GoalChecker()
        self.leaderboard_manager = LeaderboardManager()

    def check_and_update_progress(
        self, update_db: bool = True
    ) -> Tuple[List[UserToTag], List[LeaderboardEntry], bool]:
        """
        Main method to check progress and update database.
        Returns: (users_to_tag, leaderboard, is_monday)
        """
        db = self.db_manager.get_db()
        today = datetime.now()
        is_monday = today.weekday() == 0
        current_date = today.strftime("%Y-%m-%d")

        # Initialize weekly points if needed
        db = self.db_manager.initialize_weekly_points(db)

        # Handle Monday leaderboard and reset
        leaderboard = []
        if is_monday:
            leaderboard = self.leaderboard_manager.get_weekly_leaderboard(db)
            if update_db:
                db = self.db_manager.reset_weekly_points(db)

        # Process each user
        points_gained_by_user = {}

        for username, user_data in db.items():
            try:
                lc_id = user_data["lc_id"]
                fetched_stats = self.leetcode_api.get_user_stats(lc_id)

                if fetched_stats is None:
                    print(f"Failed to fetch stats for {username}")
                    points_gained_by_user[username] = 0  # Set to 0 for failed API calls
                    continue

                # Calculate points
                previous_points = user_data.get("points", 0)
                current_points = self.points_calculator.calculate_points(fetched_stats)
                points_gained = self.points_calculator.calculate_points_gained(
                    current_points, previous_points
                )
                points_gained_by_user[username] = points_gained

                print(f"{username} has gained {points_gained} points")

                # Update database if requested
                if update_db:
                    db = self.db_manager.update_user_stats(
                        db,
                        username,
                        fetched_stats["easySolved"],
                        fetched_stats["mediumSolved"],
                        fetched_stats["hardSolved"],
                        current_points,
                        points_gained,
                    )

            except Exception as e:
                print(f"Error processing {username}: {e}")
                continue

        # Clear expired goals and save database
        if update_db:
            db = self.db_manager.clear_expired_goals(db, current_date)
            self.db_manager.save_db(db)

        # Get users to tag based on goals
        users_to_tag = self.goal_checker.get_users_to_tag(
            db, points_gained_by_user, current_date
        )

        return users_to_tag, leaderboard, is_monday
