import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
import sqlite3
import logging
from datetime import datetime, timezone
from discord import ui, Interaction


async def welcome_message():
    # Find the #welcome channel
    welcome_channel_id = int(os.getenv('WELCOME_CHANNEL_ID'))
    welcome_channel = discord.utils.get(client.get_all_channels(), id=welcome_channel_id)

    # Check if welcome message has already been sent in the channel
    async for message in welcome_channel.history(limit=100):
        if message.author == client.user and message.embeds:
            print(f'Welcome message found. Message ID: {message.id}')
            return  # If the welcome message is found, exit the function

    # Send welcome message in the #welcome channel
    print(f'No welcome message found, creating one now')
    view = discord.ui.View()
    button = discord.ui.Button(label="Complete Onboarding")
    view.add_item(button)
    embed = discord.Embed(title="Welcome to the Server!", description="Here's how to get started:")
    # embed.set_thumbnail(url=ctx.guild.icon)
    embed.add_field(name="Step 1:",
                    value="Read the server rules in [#rules](https://discord.com/channels/1207801896656568480/1207802982574596137) channel.")
    embed.add_field(name="Step 2:",
                    value="Check out some cool posts over in [#projects](https://discord.com/channels/1207801896656568480/1207807674075320390).")
    embed.add_field(name="Step 3:", value="Complete Onboarding procedure to unlock the rest of the server.")
    embed.set_footer(text="Enjoy your stay!")
    await welcome_channel.send(embed=embed, view=OnboardButtons())

async def update_nickname(member, firstname, lastname):
    nickname = f"{firstname} {lastname}"
    c.execute("UPDATE members SET nickname = ?, firstname = ?, lastname = ? WHERE user_id = ?", (nickname, firstname, lastname, member.id))
    conn.commit()
    print(f'Updated... {member}, {firstname}, {lastname}, {nickname}')
    await member.edit(nick=nickname)


# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='discord.log', level=logging.INFO)

# Define intents
intents = discord.Intents.all()

# Connect to SQLite database
conn = sqlite3.connect('member_data.db')
c = conn.cursor()

# Create table with fields if it doesn't exist already
c.execute('''CREATE TABLE IF NOT EXISTS members (
            user_id INTEGER PRIMARY KEY, 
            username TEXT, nickname TEXT, 
            firstname TEXT, lastname TEXT,
            join_datetime TEXT, 
            onboarding_status INTEGER, 
            last_change_datetime TEXT
        )''')

conn.commit()

# Initialize bot
client = commands.Bot(command_prefix='.', intents=intents)

class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or("."), intents=intents)
    async def setup_hook(self) -> None:
        self.add_view(OnboardButtons())
        #self.add_view(OnboardButtons())            #Add More views with more add_view commands.

client = PersistentViewBot()

class OnboardModal(discord.ui.Modal, title="Onboarding: "):
    first_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="First name",
        required=True,
        placeholder="John "
    )
    last_name = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Last Name",
        required=True,
        placeholder="Doe"
    )
    async def on_submit(self, interaction: discord.InteractionResponse):
        print(f'First name: {self.first_name.value}')
        print(f'Last Name: {self.last_name.value}')
        print(f'User: {self.user.id}')

        await interaction.response.defer()
        await update_nickname(member=self.user, firstname=self.first_name.value, lastname=self.last_name.value)
        #channel = interaction.guild.get_channel(WELCOME_CHANNEL_ID)
        #embed = discord.Embed(title="New Onboarding data", description=self.message.value)
        #embed.set_author(name=self.user.nick)
        #await channel.send(embed=embed)
        #await interaction.response.send_message("Thanks", ephemeral=True)
    async def on_error(self, interaction: discord.Interaction, error):
        ...

class OnboardButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Complete Onboarding", style=discord.ButtonStyle.green, custom_id="1")
    async def onboard(self, interaction: discord.InteractionResponse, button: discord.ui.Button):
        onboard_modal = OnboardModal()
        onboard_modal.user = interaction.user
        await interaction.response.send_modal(onboard_modal)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await welcome_message()
    try:
        synced = await client.tree.sync()
        print(f'Slash Commands Synced. {str(len(synced))} Total Commands {synced}')
    except Exception as e:
        print(e)


@client.event
async def on_member_join(member):
    await welcome_message()
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


@client.event
async def on_member_remove(member):
    # Log member leave
    logging.info(f'Member {member.name} left the server.')


# Load bot token and welcome channel id from .env file
TOKEN = os.getenv('BOT_TOKEN')
WELCOME_CHANNEL_ID = os.getenv('WELCOME_CHANNEL_ID')

# Start bot
client.run(TOKEN)
