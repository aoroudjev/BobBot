# BobBot

## What's This?
Community support bot, meet Bob.

## How to Set It Up
1. Get Python (3.8+). Must be < 3.13
2. Install .toml requirements
3. Add your bot token as an environment variable: SEE DISCORD PINS

## How to Run It
1. Change the prefix symbol to something unique.
2. Run bot.py
3. Use `<selected-prefix>test` to check if it's working.

## Commands
- `!test` - Sends a response.
- `!update` - Updates the running bot to the latest commit and overwrites the process.

## Restrictions
- Python 3.13 removes a discordpy dependency from the std lib (audioop).
- Must keep the main entry point named ```main.py```.
