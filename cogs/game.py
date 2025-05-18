import discord
from discord import app_commands
from discord.ext import commands
import os
from util import *

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="snipe", description="Snipe a player!")
    @app_commands.describe(player="Select the player to snipe")
    async def snipe(self, interaction: discord.Interaction, player: discord.Member):
        """
        Command called when player wishes to submit a snipe of another player
        Game rules indicate an image must precede or follow this command featuring the snipe

        Args:
            player (discord.Member): The target being sniped

        Returns:
            Ephemeral message to the target requesting confirmation of snipe
        """
        guild_id = interaction.guild.id

        data = load_data(guild_id)
        target_id = str(player.id)
        sniper_id = str(interaction.user.id)

        if sniper_id not in data["users"]:
            await interaction.response.send_message("You are not in the game!", ephemeral=True)
            return

        if target_id not in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is not in the game!", ephemeral=True)
            return
        if target_id == sniper_id:
            await interaction.response.send_message("You can't snipe yourself!", ephemeral=True)
            return
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))