import json
import requests
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

# Discord setup
intents = discord.Intents.default()
intents.members = True  # Need members intent to look up members by name
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))  # Channel to send reminders


def get_db():
    with open("db.json", "r") as f:
        return json.load(f)


def save_db(db):
    with open("db.json", "w") as f:
        json.dump(db, f, indent=4)


def check_leetcode_progress():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    users_to_tag = []

    for username, user_data in db.items():
        # Skip if user doesn't have necessary data
        if not all(key in user_data for key in ["lc_id", "goal", "solved"]):
            continue

        # Check if goal is active
        goal_end_date = user_data["goal"][1]
        daily_goal = user_data["goal"][0]

        if today < goal_end_date:
            # Goal is active, check LeetCode progress
            lc_id = user_data["lc_id"]
            previous_solved = user_data["solved"]

            try:
                # Make request to LeetCode API
                response = requests.get(
                    f"https://alfa-leetcode-api.onrender.com/{lc_id}/solved"
                )
                response.raise_for_status()
                data = response.json()

                current_solved = data["solvedProblem"]

                # Update the solved count in the database
                problems_solved_since_last_check = current_solved - previous_solved

                if problems_solved_since_last_check < daily_goal:
                    # User hasn't met their goal
                    users_to_tag.append(
                        (username, daily_goal, problems_solved_since_last_check)
                    )

                # Update the solved count in the database
                db[username]["solved"] = current_solved

            except Exception as e:
                print(f"Error checking progress for {username}: {e}")
        elif today == goal_end_date:
            # Today is the last day of the goal, set goal to empty array
            lc_id = user_data["lc_id"]
            previous_solved = user_data["solved"]

            try:
                # Make request to LeetCode API
                response = requests.get(
                    f"https://alfa-leetcode-api.onrender.com/{lc_id}/solved"
                )
                response.raise_for_status()
                data = response.json()

                current_solved = data["solvedProblem"]

                # Update the solved count in the database
                problems_solved_since_last_check = current_solved - previous_solved

                if problems_solved_since_last_check < daily_goal:
                    # User hasn't met their goal
                    users_to_tag.append(
                        (username, daily_goal, problems_solved_since_last_check)
                    )

                # Update the solved count in the database
                db[username]["solved"] = current_solved
                # Set goal to empty array
                db[username]["goal"] = []

            except Exception as e:
                print(f"Error checking progress for {username}: {e}")

    # Save updated database
    save_db(db)
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
    users_to_tag = check_leetcode_progress()

    if users_to_tag:
        for username, goal, actual in users_to_tag:
            # Try to find the member in the guild by their username
            member = discord.utils.get(guild.members, name=username)

            if member:
                # Use proper Discord mention format with member ID
                word = "leetcode" if goal == 1 else "leetcodes"
                await channel.send(
                    f"@everyone this is why <@{member.id}> is unemployed. They've failed to do their {goal} {word} today"
                )
            else:
                # Fallback if member not found
                print(f"Could not find member with username: {username}")
    else:
        print("No reminders needed")

    # Close the bot after sending messages
    await bot.close()


if __name__ == "__main__":
    bot.run(TOKEN)
