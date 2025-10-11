import asyncio
from datetime import datetime, time
from zoneinfo import ZoneInfo
from discord import Interaction
import discord
from discord.app_commands import CheckFailure
from utils.util_db import get_config
from models import *
import random

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
    await interaction.response.send_message(get_init_saying(), ephemeral=True)
    config = get_config(guild_id)
    if not config:
        raise GameNotInitialized("Game is not Initialized!")
    if not config.safe_times:
        return True

    now = datetime.now(PACIFIC)
    weekday = now.weekday()

    for safetime in config.safe_times:
        if safetime.day != weekday:
            continue

        buffer = timedelta(minutes=15)
        start_buf = datetime.combine(now.date(), safetime.start_time) - buffer
        end_buf = datetime.combine(now.date(), safetime.end_time) + buffer
        if start_buf <= now <= end_buf:
            raise NowSafeTime("Cannot Snipe during a safetime!")
    return True


def get_init_saying():
    sayings = [
        "Aiming down sights...",
        "Locking on target...",
        "Loading round...",
        "Tracking movement...",
        "Lining up the shot...",
        "Scope calibrated.",
        "Sniper breathing steady...",
        "Camouflage engaged...",
        "Target acquired.",
        "Finger on the trigger...",
        "Weapon primed and ready.",
        "Tactical advantage: established.",
        "Snipe feed locked in.",
        "Engaging sniping protocol..."
    ]
    return random.choice(sayings)
