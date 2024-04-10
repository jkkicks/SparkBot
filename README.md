# SparkBot

A Discord bot for Spark Studio Salem

## Prerequisites

- Go to https://discord.com/developers/applications and make an application
- Go to the Bot page.
- Copy `env.dist` to `.env` and add the Bot Token to this file.
- Choose what channels you want the bot to operate in on your server and add their IDs to the file as well.

## Installation

Requires Python 3.

- Run `pip install -r requirements.txt`

## Running

Run `python3 main.py`

## Usage

### Available Commands

```
/help : to view all commands
/nick : to view current nickname
/setnick : to change nickname
/reinit : to re-initialize a user in the database (i.e. if they joined when the bot wasn't listening)
```

## Database

Initialization of the structure is automatically handled inside `main.py` and
creates the SQLITE3 file `member_data.db`.