import enum

import discord
from discord import app_commands
from discord.ext.commands import Cog as Cock, Bot


from pathlib import Path

import json
from enum import Enum

EMPLOYEE_JSON_PATH = Path(__file__, "..", "employees.json")


class Role(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    STANDARD = "STANDARD"

def _get_json_data():
    with EMPLOYEE_JSON_PATH.open("r") as file:
        return json.load(file)

def _update_json(new_data: dict):
    _get_json_data().update(new_data)
    with EMPLOYEE_JSON_PATH.open("w") as file:
        json.dump(new_data, file)


def has_role(user_id, role: Role):
    """Checks if user has role"""
    return _get_json_data()[user_id]["roles"].__contains__(role.value)

async def send_message(interaction: discord.Interaction, message):
    await interaction.response.send_message(message)


class CompanyCog(Cock):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="hire", description="Hire an employee")
    async def hire(self, interaction: discord.Interaction, user: discord.User):
        """
        Adds a mentioned user to the database if the caller is a Role.ADMIN
        """
        user_data = {
            user.id: {"id": user.id, "name": user.name, "roles": Role.ADMIN.value},
        }

        json_data = _get_json_data()

        caller_id = str(interaction.user.id)
        if caller_id not in json_data:
            return

        if not any([has_role(caller_id, Role.ADMIN), has_role(caller_id, Role.MANAGER)]):
            await send_message(interaction, "Can't do that")
            return

        if str(user.id) not in json_data.keys():
            _update_json(user_data)
            await send_message(interaction, f"You're Hired! {user.name}")
        else:
            await send_message(interaction, f"Clock in dumbass {user.name}")


    @app_commands.command(name="promote", description="promote an employee")
    async def promote(self, interaction: discord.Interaction, user: discord.User):
        json_data= _get_json_data()
        caller_id = str(interaction.user.id)

        if not any([has_role(caller_id, Role.ADMIN), has_role(caller_id, Role.MANAGER)]):
            await send_message(interaction, "Can't do that")
            return

        if has_role(str(user.id), Role.MANAGER):
            await send_message(interaction, "Already Manager")
            return

        json_data[str(user.id)]["roles"].append(Role.MANAGER.value)
        _update_json(json_data)
        await send_message(interaction, "YAY! GRATSMAN")

