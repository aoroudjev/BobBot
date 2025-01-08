import asyncio
import os
import random

import discord
from dateutil import parser
from discord.ext import commands
from discord.ui import View, Select, Button

from utils import updater

TOKEN = os.getenv("TOKEN")

TRIGGER_FILE = "update.trigger"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="$")


async def update_loop():
    while True:
        if os.path.exists(TRIGGER_FILE):
            print("Update trigger detected... Restarting")
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
    await bot.tree.sync()
    print("Ready!")
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


@bot.command()
async def meeting(ctx):
    pass


# =========Tree Commands==========


@bot.tree.command(name="event", description="Create and manage events.")
async def event(interaction: discord.Interaction):
    await interaction.response.send_message("Configure in your DM's!", ephemeral=True)
    await interaction.user.send(f"Hello {interaction.user}!")

    embed = discord.Embed(
        title="Meeting Maker", description="Let's set up your meeting step by step."
    )
    embed.add_field(
        name="Step 1: Meeting Title",
        value="Please type the meeting title.",
        inline=False,
    )

    await interaction.user.send(embed=embed)

    def check_message(m):
        return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

    # Step 1: Get Meeting Title
    title_msg = await bot.wait_for("message", check=check_message)
    meeting_title = title_msg.content

    # Step 2: Confirm Title
    confirm_embed = discord.Embed(
        title="Step 2: Confirm Title",
        description=f"Is this correct? **{meeting_title}**",
    )
    confirm_embed.set_footer(text="React with ✅ to confirm or ❌ to re-enter.")

    confirm_message = await interaction.user.send(embed=confirm_embed)
    await confirm_message.add_reaction("\u2705")  # Checkmark
    await confirm_message.add_reaction("\u274c")  # Cross

    def check_reaction(reaction, user):
        return user == interaction.user and str(reaction.emoji) in ["\u2705", "\u274c"]

    reaction, _ = await bot.wait_for("reaction_add", check=check_reaction)

    if str(reaction.emoji) == "\u274c":
        return await interaction.user.send("Let's start over. Use /event again.")

    # Step 3: Get Date (Processed by dateutil)
    await interaction.user.send(
        "Now, please enter the date and time for the meeting in any format."
    )
    date_msg = await bot.wait_for("message", check=check_message)

    try:
        interpreted_date = parser.parse(date_msg.content)
    except ValueError:
        return await interaction.user.send("Couldn't interpret the date. Please try again.")

    # Confirm Date
    date_embed = discord.Embed(
        title="Step 4: Confirm Date",
        description=f"I understood the date as: **{interpreted_date}**. Is this correct?",
    )
    date_embed.set_footer(text="React with ✅ to confirm or ❌ to re-enter.")

    date_message = await interaction.user.send(embed=date_embed)
    await date_message.add_reaction("\u2705")
    await date_message.add_reaction("\u274c")

    reaction, _ = await bot.wait_for("reaction_add", check=check_reaction)

    if str(reaction.emoji) == "\u274c":
        return await interaction.user.send("Let's start over. Use /event again.")

    # Final Confirmation
    final_embed = discord.Embed(
        title="Meeting Created!",
        description=f"**Title:** {meeting_title}\n**Date and Time:** {interpreted_date}",
    )
    await interaction.user.send(embed=final_embed)

    # Optionally announce the event in a specific channel
    channel = discord.utils.get(interaction.guild.text_channels, name="events")
    if channel:
        await channel.send(embed=final_embed)


bot.run(TOKEN)
