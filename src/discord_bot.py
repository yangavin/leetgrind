import discord
from discord.ext import commands
from typing import List

from .models import UserToTag, LeaderboardEntry
from .leaderboard import LeaderboardManager


class DiscordBot:
    def __init__(self, token: str, channel_id: int):
        self.token = token
        self.channel_id = channel_id

        intents = discord.Intents.default()
        intents.members = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

    async def send_tags(self, users_to_tag: List[UserToTag]) -> None:
        """Send tag messages for users who didn't meet their goals."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"Could not find channel with ID {self.channel_id}")
            return

        guild = channel.guild

        if users_to_tag:
            for user_to_tag in users_to_tag:
                member = discord.utils.get(guild.members, name=user_to_tag.username)

                if member:
                    word = "point" if user_to_tag.daily_goal == 1 else "points"
                    await channel.send(
                        f"@everyone <@{member.id}> has failed to gain {user_to_tag.daily_goal} {word} yesterday, this is why they are unemployed"
                    )
                else:
                    print(
                        f"Could not find member with username: {user_to_tag.username}"
                    )
        else:
            print("No reminders needed")

    async def send_leaderboard(self, leaderboard: List[LeaderboardEntry]) -> None:
        """Send weekly leaderboard to Discord."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"Could not find channel with ID {self.channel_id}")
            return

        message = LeaderboardManager.format_leaderboard_message(
            leaderboard, channel.guild
        )
        await channel.send(message)

    async def connect_and_execute(self, execute_func) -> None:
        """Connect to Discord and execute the provided function."""

        @self.bot.event
        async def on_ready():
            print(f"Logged in as {self.bot.user}")
            try:
                await execute_func(self)
            finally:
                await self.bot.close()

        await self.bot.start(self.token)
