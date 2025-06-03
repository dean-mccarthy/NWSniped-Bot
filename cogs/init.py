import discord
from discord import app_commands
from discord.ext import commands
import os
from models import *
from dotenv import load_dotenv
from util import *
from typing import Literal

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))

class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="pongs")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="help", description="List all available commands")
    async def help(self, interaction:discord.Interaction):
        embed = discord.Embed(title="Sniped Bot Help", description="Here are all of my commands:", color=discord.Color.blue())

        commands = sorted(self.bot.tree.get_commands(), key=lambda cmd:cmd.name)

        for command in commands:
            embed.add_field(
                name=f"/{command.name}",
                value=command.description or "No description provided.",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

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

        result = add_player_helper(guild_id, player)
        await interaction.response.send_message(result[0], ephemeral=result[1])
        return
    
    @app_commands.command(name="joingame", description="Register yourself in the snipe game")
    async def join_game(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        result = add_player_helper(guild_id, interaction.user)
        await interaction.response.send_message(result[0], ephemeral=result[1])
        return
    

    @app_commands.command(name="resetgame", description="Resets the snipe game")
    async def reset_game(self, interaction: discord.Interaction):
        """
        Command to reset game

        Resets json file for current server
        """
        #print("Attempting to init game")
        guild_id = interaction.guild.id
        data = {"snipes": [], "users": {}}
        config = ServerConfig()
        save_data(guild_id, data)
        save_config(guild_id, config)
        await interaction.response.send_message("Game has been reset!")
        return
    
    @app_commands.command(name="config", description="Adjusts the settings of the game")
    async def config(self, interaction: discord.Interaction, setting: Literal["points_per_snipe", "penalty_per_snipe", "acheivements_enabled"], value: str):
        guild_id = interaction.guild.id
        newConf = load_config(guild_id)
        match setting:
            case "points_per_snipe":
                newConf.points_per_snipe = float(value)
                save_config(guild_id, newConf)
                await interaction.response.send_message(f"Points_per_snipe now set to {newConf.points_per_snipe}", ephemeral=True)
                return
            case "penalty_per_snipe":
                newConf.penalty_per_snipe = float(value)
                save_config(guild_id, newConf)
                await interaction.response.send_message(f"Penalty_per_snipe now set to {newConf.penalty_per_snipe}", ephemeral=True)
                return
            case "acheivements_enabled":
                if str(value) != "True" and str(value) != "False":
                    await interaction.response.send_message("Acheivements_Enabled must be `True` or `False`", ephemeral=True)
                    return
                newConf.acheivements_enabled = str(value) == "True"
                save_config(guild_id, newConf)
                await interaction.response.send_message(f"Acheivements are now {"enabled" if newConf.acheivements_enabled else "disabled"}", ephemeral=True)
                return

    
    



    
    
async def setup(bot):
    await bot.add_cog(Init(bot))
