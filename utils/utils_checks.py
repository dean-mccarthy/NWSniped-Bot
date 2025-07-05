from discord import Interaction
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