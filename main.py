import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import argparse
import sys
import asyncio

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Get guild ID from environment variable for instant command updates
GUILD_ID = int(os.getenv("GUILD_ID", "0"))  # Default to 0 if not found

# Setup command line arguments
parser = argparse.ArgumentParser(description="LeetGrind Discord Bot")
parser.add_argument(
    "--delete", action="store_true", help="Delete all commands and exit"
)
args = parser.parse_args()


# Function to delete all commands
async def delete_all_commands():
    print("Deleting all commands...")

    # Login to Discord first
    await bot.login(os.getenv("DISCORD_TOKEN"))

    # Delete guild commands if GUILD_ID is available
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"Cleared all commands from guild {GUILD_ID}")

    # Delete global commands - must use None for guild parameter
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    print("Cleared all global commands")

    print("All commands deleted. Exiting.")
    await bot.close()


def get_db():
    with open("db.json", "r") as f:
        db = json.load(f)
    return db


def save_db(db):
    with open("db.json", "w") as f:
        json.dump(db, f, indent=4)


# This runs once when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        if GUILD_ID:
            # For instant command updates, sync to specific guild
            guild = discord.Object(id=GUILD_ID)
            # Clear all commands for this guild first
            bot.tree.clear_commands(guild=guild)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(
                f"Refreshed and synced {len(synced)} slash commands to guild {GUILD_ID}."
            )
        else:
            # Global sync (slower updates)
            # Clear all global commands first
            bot.tree.clear_commands(guild=None)
            synced = await bot.tree.sync()
            print(f"Refreshed and synced {len(synced)} slash commands globally.")
    except Exception as e:
        print(e)


@bot.tree.command(name="getgoal", description="Get your current goal")
async def get_goal(interaction: discord.Interaction):
    db = get_db()
    user_name = f"{interaction.user.name}"

    if user_name not in db:
        await interaction.response.send_message(
            "You haven't set a goal yet. Use /setgoal to set one!"
        )
        return

    if "goal" not in db[user_name] or not db[user_name]["goal"]:
        await interaction.response.send_message(
            "You don't have any on-going goals. Use /setgoal to set one!"
        )
        return

    user_goal = db[user_name]["goal"]
    points_is_one = user_goal[0] == 1

    await interaction.response.send_message(
        f"Your current goal is {user_goal[0]} point{'' if points_is_one else 's'} until {user_goal[1]}"
    )


@bot.tree.command(name="setgoal", description="Set your goal")
async def set_goal(
    interaction: discord.Interaction,
    points: app_commands.Range[int, 1, None],
    days: int,
):
    db = get_db()
    user_name = f"{interaction.user.name}"

    # Calculate the end date
    end_date_dt = datetime.now() + timedelta(days=days)
    end_date = end_date_dt.strftime("%Y-%m-%d")

    # Check if user already has a goal and if new end date is earlier
    if (
        user_name in db and "goal" in db[user_name] and db[user_name]["goal"]
    ):  # Only validate if goal exists and is not empty
        current_end_date = db[user_name]["goal"][1]
        current_end_date_dt = datetime.strptime(current_end_date, "%Y-%m-%d")
        if end_date_dt < current_end_date_dt:
            await interaction.response.send_message(
                f"nice try, you cannot change your goal to end earlier than {current_end_date}"
            )
            return

    # Create user entry if doesn't exist
    if user_name not in db:
        db[user_name] = {}

    # Set the goal
    db[user_name]["goal"] = [points, end_date]

    # Save the updated database
    save_db(db)

    points_is_one = points == 1
    await interaction.response.send_message(
        f"Goal set! You are to gain {points} point{'' if points_is_one else 's'} daily until {end_date}"
    )


@bot.tree.command(
    name="help", description="Get help with LeetGrind bot commands and point system"
)
async def help_command(interaction: discord.Interaction):
    help_text = """
**LeetGrind Bot Help**

**Points System:**
- Easy LeetCode problems = 1 point
- Medium LeetCode problems = 2 points
- Hard LeetCode problems = 3 points

**Commands:**
- `/setgoal <points> <days>` - Set a daily points goal for the specified number of days
- `/getgoal` - View your current goal
- `/help` - Show this help message

The bot will check your LeetCode progress daily and tag you if you don't meet your goal.
"""
    await interaction.response.send_message(help_text)


# Handle command line arguments and start the bot
if args.delete:
    # Run the deletion function
    asyncio.run(delete_all_commands())
else:
    # Start the bot normally
    bot.run(os.getenv("DISCORD_TOKEN"))
