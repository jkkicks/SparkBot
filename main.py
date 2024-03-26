import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Set up logging handler. Passed in at the end in bot.run
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Load ENV file
load_dotenv()

# Gather variables from .env file
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('BOT_CHANNEL_ID'))
botCommandsEnable = True

if BOT_TOKEN is None:
    print("BOT TOKEN NOT FOUND IN ENV")
    exit()
if CHANNEL_ID is None:
    print("NO CHANNEL SELECTED, DISABLING BOT COMMANDS")
    botCommandsEnable = False
else:
    print(f'Channel ID selected: {CHANNEL_ID}')


intents = discord.Intents.all()
intents.members = True  # Enable the member update intent
intents.message_content = True  # Enable the Privileged Content intent

# Set discord end bot commands to / prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# Connect to SQLite
conn = sqlite3.connect('member_data.db')
cursor = conn.cursor()

# Create Dataset if it doesn't exist already
cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        nickname TEXT,
        join_date TEXT
    )
''')
conn.commit()


@bot.event
async def on_ready():
    # When API connects and logs in.
    print(f'Bot logged in as {bot.user.name}')

    # Send help command to bot-commands channel
    # channel = bot.get_channel(int(CHANNEL_ID))
    # await channel.send(f'Use /help to view available commands')


@bot.event
async def on_member_join(member):
    # Print user's name and ID in the console on new join
    print(f'New member joined: {member.name} (ID: {member.id}), joined at {member.joined_at}')
    print(member)

    # Store member data in the database
    cursor.execute('INSERT INTO members (user_id, username, join_date) VALUES (?, ?, ?)',
                   (member.id, member.name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()


@bot.command()
async def commands(ctx):
    avail_commands = open("availcommands.txt", "r")
    await ctx.send(avail_commands.read())
    avail_commands.close()


@bot.command()
async def setnick(ctx, new_nickname: str):

        # Update user's nickname in the database
        cursor.execute('UPDATE members SET nickname = ? WHERE user_id = ?', (new_nickname, ctx.author.id))
        conn.commit()

        # Retrieve the updated nickname from the database
        cursor.execute('SELECT nickname FROM members WHERE user_id = ?', (ctx.author.id,))
        updated_nickname = cursor.fetchone()[0]

        # Print the updated nickname to the console
        print(f'Nickname updated for {ctx.author.name} (ID: {ctx.author.id}): {updated_nickname}')

        member = ctx.guild.get_member(ctx.author.id)
        if member:
            try:
                await member.edit(nick=updated_nickname)
                print(f'Nickname updated on the server for {ctx.author.name}')
            except discord.Forbidden:
                print(f'Failed to update nickname on the server for {ctx.author.name}: Missing permissions')
            except discord.HTTPException as e:
                print(f'Failed to update nickname on the server for {ctx.author.name}: {e}')

# Close the database connection when the bot is stopped
@bot.event
async def on_disconnect():
    conn.close()

bot.run(BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)
