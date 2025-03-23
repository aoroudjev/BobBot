import datetime
from datetime import datetime
from typing import Optional
from dateutil import parser

import discord
from discord import User, DMChannel, app_commands
from discord.ext import commands


class EventCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def message_check(self, user):
        """Check if correct DM channel"""
        return lambda m: m.author == user and isinstance(m.channel, DMChannel)

    def reaction_check(self, user: User, valid_reactions: list[str]):
        """Check if user reacted with given reactions"""
        return (
            lambda reaction, reactor: reactor == user
            and str(reaction.emoji) in valid_reactions
        )

    async def get_user_input(
        self, user: User, prompt: str, embed: discord.Embed = None
    ) -> discord.Message:
        """Send message and wait for user text reply"""
        if embed:
            await user.send(embed=embed)
        else:
            await user.send(prompt)

        return await self.bot.wait_for("message", check=self.message_check(user))

    async def get_user_confirmation(
        self, user: User, prompt: str, embed: discord.Embed = None
    ):
        """Send message and wait for user reaction reply"""
        if embed:
            message = await user.send(embed=embed)
        else:
            message = await user.send(prompt)

        await message.add_reaction("✅")
        await message.add_reaction("❌")

        reaction, _ = await self.bot.wait_for(
            "reaction_add", check=self.reaction_check(user, ["✅", "❌"])
        )
        return str(reaction.emoji) == "✅"

    def get_time_and_date(self, prompt:str ='Now') -> Optional[datetime]:
        try:
            date_time = parser.parse(prompt)
        except ValueError:
            return None
        return date_time


    @app_commands.command(name="event", description="Create and manage events.")
    async def event(self, interaction: discord.Interaction):
        """Main meeting setup process"""

        # Needed info
        title = ''
        date_time: datetime = datetime.now()
        roles: list[discord.Role] = None
        notify = True

        await interaction.response.send_message("Configure in your DM's!", ephemeral=True)
        await interaction.user.send(f"Hello {interaction.user}!")

        # Step 1. Title
        embed = discord.Embed(
            title="Meeting Maker",
            description="Let's set up your meeting step by step.",
        )
        embed.add_field(
            name="Step 1: Meeting Title",
            value="Please type the meeting title.",
            inline=False,
        )

        response = await self.get_user_input(interaction.user, None, embed)
        title = response.content

        # Step 2. Get Date
        embed = discord.Embed(
            title="Meeting Maker",
            description="Let's set up your meeting step by step.",
        )
        embed.add_field(
            name="Step 2: Date & Time",
            value="Please type a date and time.",
            inline=False,
        )
        embed.add_field(
            name="Examples",
            value="15th at 10pm\nDec 16 6pm\n18 7pm\nmonday 7pm",
            inline=False,
        )
        embed.set_footer(text="Note: relative days like today and tomorrow doesn't work")
        response = await self.get_user_input(interaction.user, None, embed)
        date_time = self.get_time_and_date(response.content)



        embed = discord.Embed(
            title="Confirmation",
            description="Please check the details below for confirmation",
        )
        embed.add_field(
            name="Settings",
            value=f"Title: {title}\nDate/Time: {date_time}\n",
            inline=False,
        )
        embed.set_footer(text="React with ✅ to confirm or ❌ to re-enter.")

        await self.get_user_confirmation(interaction.user, None, embed=embed)



        pass
