from .models import UserStats, PROBLEM_SCALE


class PointsCalculator:
    @staticmethod
    def calculate_points(stats: UserStats) -> int:
        """Calculate total points based on solved problems."""
        return (
            stats["easySolved"] * PROBLEM_SCALE["easy"]
            + stats["mediumSolved"] * PROBLEM_SCALE["medium"]
            + stats["hardSolved"] * PROBLEM_SCALE["hard"]
        )

    @staticmethod
    def calculate_points_gained(current_points: int, previous_points: int) -> int:
        """Calculate points gained since last check."""
        return max(0, current_points - previous_points)  # Ensure non-negative
