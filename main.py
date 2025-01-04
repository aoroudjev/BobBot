import asyncio
import os


import discord
from discord.ext import commands

from utils import updater

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(intents=intents, command_prefix="!")

TRIGGER_FILE = 'update.trigger'

async def update_loop():
    while True:
        if os.path.exists(TRIGGER_FILE):
            print("Update trigger detected... running update script.")
            os.remove(TRIGGER_FILE)
            updater.restart_program()
        await asyncio.sleep(10)

# =========Events==========
@bot.event
async def on_message(message) -> None:
    """Spawns on ANY message in overseen channels regardless of prefix."""
    await bot.process_commands(message)


@bot.event
async def on_error(event, *args) -> None:
    """Log on error."""
    with open("err.log", "a") as f:
        f.write(f"Error: {args[0]}\n")


@bot.event
async def on_ready() -> None:
    """On start of bot."""
    print(bot.guilds)
    guild = discord.utils.get(bot.guilds)
    print(f"{bot.user} is connected to the following guild: {guild}")

    # Start the update loop as an async task
    bot.loop.create_task(update_loop())


# =========Commands==========
@bot.command()
async def test(ctx) -> None:
    """Test command to check bot connectivity/functionality."""
    await ctx.channel.send("Response! v3")


@bot.command()
async def update(ctx) -> None:
    """Force update bot, don't wait for trigger."""
    try:
        updater.update_self()
        await ctx.channel.send("Done updating!")
        await bot.close()
    except Exception:
        raise

@bot.command()
async def echo(ctx, *args) -> None:
    await ctx.channel.send(" ".join(args))


bot.run(TOKEN)
