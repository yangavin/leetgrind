from datetime import datetime
from typing import List, Dict, Optional

from .models import UserData, UserToTag


class GoalChecker:
    @staticmethod
    def has_active_goal(user_data: UserData) -> bool:
        """Check if user has an active goal."""
        goal = user_data.get("goal")
        return goal is not None and len(goal) >= 2

    @staticmethod
    def is_goal_expired(user_data: UserData, current_date: str) -> bool:
        """Check if user's goal is expired."""
        if not GoalChecker.has_active_goal(user_data):
            return True

        goal_end_date = user_data["goal"][1]
        return current_date > goal_end_date

    @staticmethod
    def get_daily_goal(user_data: UserData) -> Optional[int]:
        """Get user's daily goal points."""
        if not GoalChecker.has_active_goal(user_data):
            return None
        return user_data["goal"][0]

    @staticmethod
    def check_goal_achievement(points_gained: int, daily_goal: int) -> bool:
        """Check if user has achieved their daily goal."""
        return points_gained >= daily_goal

    @staticmethod
    def get_users_to_tag(
        db: Dict[str, UserData],
        points_gained_by_user: Dict[str, int],
        current_date: str,
    ) -> List[UserToTag]:
        """Get list of users who should be tagged for not meeting their goals."""
        users_to_tag = []

        for username, user_data in db.items():
            # Skip users without active goals
            if not GoalChecker.has_active_goal(user_data):
                print(f"Skipping {username} because goal is not active")
                continue

            # Skip users with expired goals
            if GoalChecker.is_goal_expired(user_data, current_date):
                print(f"Skipping {username} because goal is expired")
                continue

            daily_goal = GoalChecker.get_daily_goal(user_data)
            points_gained = points_gained_by_user.get(username, 0)

            if not GoalChecker.check_goal_achievement(points_gained, daily_goal):
                users_to_tag.append(UserToTag(username=username, daily_goal=daily_goal))
                print(
                    f"{username} needs to be tagged (gained {points_gained}, needed {daily_goal})"
                )
            else:
                print(
                    f"{username} met their goal (gained {points_gained}, needed {daily_goal})"
                )

        return users_to_tag
