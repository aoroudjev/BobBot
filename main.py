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
    """On start of bot"""
    print(bot.guilds)
    guild = discord.utils.get(bot.guilds)
    print(f"{bot.user} is connected to the following guild: {guild}")


# =========Commands==========
@bot.command()
async def test(ctx) -> None:
    """Test command to check bot connectivity/functionality"""
    await ctx.channel.send("Response! v3")


@bot.command()
async def update(ctx) -> None:
    await ctx.channel.send("Updating... brb")
    try:
        updater.update_self()
        await ctx.channel.send("Done updating!")
        await bot.close()
    except Exception:
        raise


bot.run(TOKEN)
