import os
import argparse
from dotenv import load_dotenv

from src.leetcode_service import LeetCodeService
from src.discord_bot import DiscordBot

load_dotenv()

# Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0").split()[0])
LEETCODE_API_URL = os.getenv("LEETCODE_API_URL")


async def execute_bot_logic(discord_bot: DiscordBot):
    """Execute the main bot logic."""
    service = LeetCodeService(LEETCODE_API_URL, "db.json")
    users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
        update_db=True
    )

    # Send Monday leaderboard if applicable
    if is_monday and leaderboard:
        await discord_bot.send_leaderboard(leaderboard)

    # Send tags for users who didn't meet goals
    await discord_bot.send_tags(users_to_tag)


def main():
    parser = argparse.ArgumentParser(description="Check LeetCode progress")
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the progress without updating the database",
    )
    args = parser.parse_args()

    if args.print:
        # Print mode - just show who would be tagged
        service = LeetCodeService(LEETCODE_API_URL, "db.json")
        users_to_tag, leaderboard, is_monday = service.check_and_update_progress(
            update_db=False
        )

        if is_monday and leaderboard:
            print("=== Weekly Leaderboard ===")
            for i, entry in enumerate(leaderboard, 1):
                print(f"{i}. {entry.username}: {entry.points} points")
            print()

        if users_to_tag:
            print("Users to tag:")
            for user_to_tag in users_to_tag:
                print(f"{user_to_tag.username}: needs {user_to_tag.daily_goal} points")
        else:
            print("No users to tag")
    else:
        # Discord bot mode
        discord_bot = DiscordBot(TOKEN, CHANNEL_ID)
        import asyncio

        asyncio.run(discord_bot.connect_and_execute(execute_bot_logic))


if __name__ == "__main__":
    main()
