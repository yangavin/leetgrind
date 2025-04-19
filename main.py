import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Get guild ID from environment variable for instant command updates
GUILD_ID = int(os.getenv("GUILD_ID", "0"))  # Default to 0 if not found


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
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} slash commands to guild {GUILD_ID}.")
        else:
            # Global sync (slower updates)
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} slash commands globally.")
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
    leetcode_is_one = user_goal[0] == 1

    await interaction.response.send_message(
        f"Your current goal is {user_goal[0]} daily leetcode{'' if leetcode_is_one else 's'} until {user_goal[1]}"
    )


@bot.tree.command(name="setgoal", description="Set your goal")
async def set_goal(
    interaction: discord.Interaction,
    leetcode: app_commands.Range[int, 1, None],
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
    db[user_name]["goal"] = [leetcode, end_date]

    # Save the updated database
    save_db(db)

    leetcode_is_one = leetcode == 1
    await interaction.response.send_message(
        f"Goal set! You are to complete {leetcode} daily leetcode{'' if leetcode_is_one else 's'} until {end_date}"
    )


# Start the bot
bot.run(os.getenv("DISCORD_TOKEN"))
