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
creates the SQLITE3 file `member_data.db`. An example file is included in this repo

## Contributions

Thank you for considering contributing to our project! We welcome contributions from everyone. Before making any changes, we encourage you to check the [GitHub issues](https://github.com/jkkicks/SparkBot/issues) to see if the feature or bug you're interested in has already been discussed or if someone else is already working on it.

If you don't find the issue you're interested in, feel free to open a new one to start a discussion or let others know what you're working on. This helps avoid duplicate work and ensures that everyone's efforts are aligned with the project's goals.

We follow a few guidelines to ensure that contributions are high quality and beneficial to all users:

- **Fork the Repository:** If you're planning to contribute, fork the repository and make your changes in a feature branch.
- **Submit a Pull Request:** Once your changes are ready, submit a pull request to the main repository's `main` branch. Be sure to include a clear description of your changes and why they are beneficial.
- **Code Style:** Follow the existing code style and conventions used in the project.
- **Tests:** If applicable, write tests for your changes to ensure they work as expected and don't introduce regressions.
- **Documentation:** Update the README.md or any relevant documentation to reflect your changes if needed.

By contributing to this project, you agree to license your contributions under the same license as the project itself.

Thank you for helping make our project better!
