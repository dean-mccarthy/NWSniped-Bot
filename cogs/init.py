import discord
from discord import app_commands
from discord.ext import commands
import os
from util import *

class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="pongs")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="initgame", description="Initialize the snipe game")
    async def init_game(self, interaction: discord.Interaction):
        """
        Command to initialize game

        Initializes json file for current server if one does not exist already
        """
        #print("Attempting to init game")
        guild_id = interaction.guild.id
        if os.path.exists(get_filename(guild_id)):
            data = load_data(guild_id)
            if "users" in data or "snipes" in data:
                await interaction.response.send_message("Game already exists!", ephemeral=True)
                return

        data = {"snipes": [], "users": {}}
        config = ServerConfig()
        save_data(guild_id, data)
        save_config(guild_id, config)

        await interaction.response.send_message("Game has been initialized!")

    @app_commands.command(name="addplayer", description="Register a player in the snipe game")
    @app_commands.describe(player="Select the player to add")
    async def add_player(self, interaction: discord.Interaction, player: discord.Member):
        guild_id = interaction.guild.id

        if not os.path.exists(get_filename(guild_id)):
            await interaction.response.send_message("Game is not initialized!")
            return
            
        data = load_data(guild_id)
        user_id = str(player.id)

        if user_id in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is already registered.", ephemeral=True)
            return

        data["users"][user_id] = User()
        save_data(guild_id, data)
        await interaction.response.send_message(f"{player.mention} has been added to the game!")
        return
    

    @app_commands.command(name="reset", description="Resets the snipe game")
    async def reset_game(self, interaction: discord.Interaction):
        """
        Command to initialize game

        Initializes json file for current server if one does not exist already
        """
        #print("Attempting to init game")
        guild_id = interaction.guild.id
        data = {"snipes": [], "users": {}}
        config = {
            "points_per_snipe": 1.0,
            "penalty_per_snipe": 1.0,
            "achievements_enabled": True
        }
        save_data(guild_id, data)
        save_config(guild_id, config)
        await interaction.response.send_message("Game has been initialized!")
    
async def setup(bot):
    await bot.add_cog(Init(bot))

