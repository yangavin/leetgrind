import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# This runs once when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)


# Define a simple slash command
@bot.tree.command(name="hello", description="Say hi to the bot!")
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey there, {interaction.user.name}!")


# Start the bot
bot.run(os.getenv("DISCORD_TOKEN"))
