from typing import List, Dict
import discord

from .models import UserData, LeaderboardEntry


class LeaderboardManager:
    @staticmethod
    def get_weekly_leaderboard(db: Dict[str, UserData]) -> List[LeaderboardEntry]:
        """Get sorted list of users and their weekly points."""
        leaderboard = [
            LeaderboardEntry(username=username, points=data["weekly_points"])
            for username, data in db.items()
        ]
        return sorted(leaderboard, key=lambda x: x.points, reverse=True)

    @staticmethod
    def format_leaderboard_message(leaderboard: List[LeaderboardEntry], guild) -> str:
        """Format the leaderboard message for Discord."""
        if not leaderboard:
            return "No points scored this week!"

        message = "# 🏆 Leaderboard 🏆\n"

        # Add users with points
        for i, entry in enumerate(leaderboard, 1):
            if entry.points > 0:
                member = discord.utils.get(guild.members, name=entry.username)
                mention = f"<@{member.id}>" if member else entry.username
                message += f"{i}. {mention} - `{entry.points} pts`\n"

        # Add users with 0 points
        zero_point_users = [
            entry.username for entry in leaderboard if entry.points == 0
        ]
        if zero_point_users:
            message += "\n0 points and will forever be unemployed:\n"
            mentions = []
            for username in zero_point_users:
                member = discord.utils.get(guild.members, name=username)
                mention = f"<@{member.id}>" if member else username
                mentions.append(mention)
            message += " ".join(mentions)

        return message
