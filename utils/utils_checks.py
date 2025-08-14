import asyncio
from datetime import datetime, time
from zoneinfo import ZoneInfo
from discord import Interaction
import discord
from discord.app_commands import CheckFailure
from utils.util_db import get_config
from models import *

PACIFIC = ZoneInfo("Canada/Pacific")


class GameNotInitialized(CheckFailure):
    pass

class MissingControlRole(CheckFailure):
    pass

class NowSafeTime(CheckFailure):
    pass

async def check_initialized(interaction: Interaction):
    if not interaction.guild:
        raise GameNotInitialized("Guild not found")

    config = get_config(interaction.guild.id)
    if not config:
        raise GameNotInitialized("Game is not Initialized!")
    return True

async def check_perms(interaction: Interaction):
    allowed_roles = {"Sniped Control", "Admin"}
    if any(role.name in allowed_roles for role in interaction.user.roles):
        return True
    
    if ( interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator):
        return True
    raise MissingControlRole("You don't have permission to use this command.")


async def safe_send(interaction: Interaction, content: str, ephemeral: bool = True):
    try:
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(content, ephemeral=ephemeral)
    except Exception as e:
        print(f"[safe_send] Failed to respond: {e}")



async def make_role(guild: discord.Guild) -> discord.Role | None:
    await asyncio.sleep(2)
    print(f"Bot permissions in {guild.name}: {guild.me.guild_permissions}")
    role_name = "Sniped Control"
    
    # Check if the role already exists
    existing_role = discord.utils.get(guild.roles, name=role_name)
    if existing_role:
        print(f"Role '{role_name}' already exists in {guild.name}")
        return existing_role

    try:

        # Create the role
        new_role = await guild.create_role(
            name=role_name
        )
        print(f"Created role '{new_role.name}' in {guild.name}")

        owner = guild.owner
        if owner:
            await owner.add_roles(new_role, reason="Auto-granted Sniped Control to server owner")
            print(f"✅ Assigned '{role_name}' to {owner.display_name} in {guild.name}")
        
        return new_role
            
    except Exception as e:
        print(f"Failed to create role in {guild.name}: {e}")
        return None


async def validate_time_format(timestr: str) -> bool:
    try:
        time = datetime.strptime(timestr, "%H:%M").time()
        return time
    except ValueError:
        return None
    
async def check_safetime(interaction: Interaction) -> bool:
    guild_id = interaction.guild.id
    config = get_config(guild_id)
    if not config:
        raise GameNotInitialized("Game is not Initialized!")
    if not config.safe_times:
        return True
    now = datetime.now(PACIFIC)
    # print(now)
    # for safetime in config.safe_times:
    #     print(safetime.start_time, safetime.end_time)
    #     print(safetime.start_time <= now, safetime.end_time >= now)

    if any (safetime.check_safe(now) for safetime in config.safe_times):
        raise NowSafeTime("Cannot Snipe during a safetime!")
    return True
