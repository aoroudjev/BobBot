import asyncio
import os
import random

import discord
from dateutil import parser
from discord.ext import commands
from discord.ui import View, Select, Button

from cogs.event_cog import EventCog

from utils.updater import update_loop

TOKEN = os.getenv("TOKEN")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="$")



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
    await bot.add_cog(EventCog(bot))
    print(f"Ready! {bot.user}")
    await bot.tree.sync()
    print("Bot is synced.")
    # Start the update loop as an async task
    bot.loop.create_task(update_loop())


# =========Commands==========

@bot.command()
async def test(ctx) -> None:
    """Test command to check bot connectivity/functionality."""
    await ctx.channel.send("Response! v3")


@bot.command()
async def echo(ctx, *args) -> None:
    await ctx.channel.send(" ".join(args))


@bot.command()
async def roll(ctx, max_roll: int = 100) -> None:
    rand_roll = int(random.random() * max_roll)
    await ctx.channel.send(rand_roll)


bot.run(TOKEN)
