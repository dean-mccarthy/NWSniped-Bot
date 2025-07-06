import asyncio
from discord import Interaction
import discord
from discord.app_commands import CheckFailure
from utils.util_db import get_config

class GameNotInitialized(CheckFailure):
    pass

async def check_initialized(interaction: Interaction):
    if not interaction.guild:
        raise GameNotInitialized("Guild not found")

    config = get_config(interaction.guild.id)
    if not config:
        raise GameNotInitialized("Game is not Initialized!")
    return True

async def safe_send(interaction: Interaction, content: str, ephemeral: bool = True):
    try:
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(content, ephemeral=ephemeral)
    except Exception as e:
        print(f"[safe_send] Failed to respond: {e}")



async def make_role(guild: discord.Guild):
    await asyncio.sleep(2)
    print(f"Bot permissions in {guild.name}: {guild.me.guild_permissions}")
    role_name = "Sniped Control"
    
    # Check if the role already exists
    existing_role = discord.utils.get(guild.roles, name=role_name)
    if existing_role:
        print(f"Role '{role_name}' already exists in {guild.name}")
        return

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
            
    except Exception as e:
        print(f"Failed to create role in {guild.name}: {e}")