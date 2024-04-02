import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import sqlite3
import logging
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='discord.log', level=logging.INFO)

# Define intents
intents = discord.Intents.all()

# Connect to SQLite database
conn = sqlite3.connect('member_data.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS members
             (user_id INTEGER PRIMARY KEY, username TEXT, nickname TEXT, join_datetime TEXT, onboarding_status INTEGER, last_change_datetime TEXT)''')

conn.commit()

# Initialize bot
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # Find the #welcome channel
    welcome_channel_id = int(os.getenv('WELCOME_CHANNEL_ID'))
    welcome_channel = discord.utils.get(bot.get_all_channels(), id=welcome_channel_id)

    # Check if welcome message has already been sent in the channel
    async for message in welcome_channel.history(limit=100):
        if message.author == bot.user and message.embeds:
            return  # If the welcome message is found, exit the function

    # Send welcome message in the #welcome channel
    view = discord.ui.View()
    button = discord.ui.Button(label="Complete Onboarding")
    view.add_item(button)
    embed = discord.Embed(title="Welcome to the Server!", description="Here's how to get started:")
    embed.add_field(name="Step 1:", value="Read the server rules in #rules channel.")
    embed.add_field(name="Step 2:", value="Check out people's projects.")
    embed.add_field(name="Step 3:", value="Complete Onboarding procedure to unlock the rest of the server.")
    embed.set_footer(text="Enjoy your stay!")
    await welcome_channel.send(embed=embed, view=view)


@bot.event
async def on_member_join(member):
    # Check if member already exists in the database
    c.execute("SELECT * FROM members WHERE user_id = ?", (member.id,))
    existing_member = c.fetchone()

    if not existing_member:  # If it's the member's first time joining
        # Add new member to the database
        c.execute(
            "INSERT OR REPLACE INTO members (user_id, username, join_datetime, onboarding_status, last_change_datetime) VALUES (?, ?, ?, ?, ?)",
            (member.id, member.name, member.joined_at.isoformat(), 0, datetime.now(timezone.utc).isoformat()))
        conn.commit()

        # Update member nickname
        await member.edit(nick=c.execute("SELECT nickname FROM members WHERE user_id = ?", (member.id,)).fetchone()[0])

        # Log member join
        logging.info(f'Member {member.name} joined the server.')


@bot.event
async def on_member_remove(member):
    # Log member leave
    logging.info(f'Member {member.name} left the server.')


# Load bot token and welcome channel id from .env file
TOKEN = os.getenv('BOT_TOKEN')
WELCOME_CHANNEL_ID = os.getenv('WELCOME_CHANNEL_ID')

# Start bot
bot.run(TOKEN)
