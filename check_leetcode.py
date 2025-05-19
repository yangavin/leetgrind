import json
import requests
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import argparse
from typing import TypedDict, List
from copy import deepcopy


load_dotenv()

# Discord setup
intents = discord.Intents.default()
intents.members = True  # Need members intent to look up members by name
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))  # Channel to send reminders
LEETCODE_API_URL = os.getenv("LEETCODE_API_URL")

problem_scale = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}


class DifficultyStat(TypedDict):
    difficulty: str
    count: int
    submissions: int


class UserStats(TypedDict):
    solvedProblem: int
    easySolved: int
    mediumSolved: int
    hardSolved: int
    totalSubmissionNum: List[DifficultyStat]
    acSubmissionNum: List[DifficultyStat]


def get_db():
    db_path = os.path.join(os.path.dirname(__file__), "db.json")
    with open(db_path, "r") as f:
        return json.load(f)


def save_db(db):
    db_path = os.path.join(os.path.dirname(__file__), "db.json")
    with open(db_path, "w") as f:
        json.dump(db, f, indent=4)


def calculate_points(stats: UserStats) -> int:
    return (
        stats["easySolved"] * problem_scale["easy"]
        + stats["mediumSolved"] * problem_scale["medium"]
        + stats["hardSolved"] * problem_scale["hard"]
    )


def check_leetcode(update_db: bool):
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    users_to_tag = []

    for username, db_user_data in db.items():
        try:
            lc_id = db_user_data["lc_id"]
            response = requests.get(f"{LEETCODE_API_URL}/{lc_id}/solved")
            response.raise_for_status()
            fetched_user_data: UserStats = response.json()

            if update_db:
                temp = deepcopy(db)
                temp[username]["easySolved"] = fetched_user_data["easySolved"]
                temp[username]["mediumSolved"] = fetched_user_data["mediumSolved"]
                temp[username]["hardSolved"] = fetched_user_data["hardSolved"]
                temp[username]["points"] = calculate_points(fetched_user_data)
                save_db(temp)

            # Check if goal is not active
            if not db_user_data["goal"] or len(db_user_data["goal"]) < 2:
                # Skip users with empty or incomplete goal lists
                print(f"Skipping {username} because goal is not active")
                continue

            goal_end_date = db_user_data["goal"][1]
            daily_goal = db_user_data["goal"][0]

            previous_points = db_user_data.get("points", 0)
            current_points = calculate_points(fetched_user_data)

            # Calculate points gained since last check
            points_gained = current_points - previous_points
            print(f"{username} has gained {points_gained} points")
            if points_gained < daily_goal:
                # User hasn't met their point goal
                users_to_tag.append((username, daily_goal))

            # If the goal is over, set the goal to an empty array
            if today > goal_end_date:
                db[username]["goal"] = []

        except Exception as e:
            print(f"Error checking progress for {username}: {e}")

    return users_to_tag


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Get the channel to send reminders
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Could not find channel with ID {CHANNEL_ID}")
        await bot.close()
        return

    # Get the guild (server) from the channel
    guild = channel.guild

    # Check progress and send reminders
    users_to_tag = check_leetcode(update_db=True)

    if users_to_tag:
        for username, goal in users_to_tag:
            # Try to find the member in the guild by their username
            member = discord.utils.get(guild.members, name=username)

            if member:
                # Use proper Discord mention format with member ID
                word = "point" if goal == 1 else "points"
                await channel.send(
                    f"@everyone <@{member.id}> has failed to gain {goal} {word} yesterday, this is why they are unemployed"
                )
            else:
                # Fallback if member not found
                print(f"Could not find member with username: {username}")
    else:
        print("No reminders needed")

    # Close the bot after sending messages
    await bot.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Check LeetCode progress")
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the progress without updating the database",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.print:
        users_to_tag = check_leetcode(update_db=False)
        if len(users_to_tag) == 0:
            print("No users to tag")
        else:
            for username, goal in users_to_tag:
                print(f"{username}: {goal}")
    else:
        bot.run(TOKEN)
