import discord
from discord import app_commands
from discord.ext import commands
import os
from models import *
from dotenv import load_dotenv
from util_db import *
from typing import Literal, Optional
from views import *

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
        check_config = get_config(guild_id)
        if check_config:
            await interaction.response.send_message("Game already exists!", ephemeral=True)
            return
        
        config = ServerConfig(guild_id=guild_id)
        save_config(config)

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
    
    @app_commands.command(name="removeplayer", description="Remove a player from the game, also removes all snipes related to player")
    @app_commands.describe(player="Select the player to remove")
    async def remove_player(self, interaction: discord.Interaction, player: discord.Member):
        """
        Command to remove player from game

        Removes a player from game and deletes all snipes related to them

        Args:
            player: discord.Member to remove from game
        """
        guild_id = interaction.guild.id

        if not get_player(guild_id, player.id):
            await interaction.response.send_message(f"{player.display_name} is not in the game.", ephemeral=True)
            return
        view = ConfirmDeleteView()
        await interaction.response.send_message(
            f"Are you sure you want to remove {player.display_name}? This action cannot be undone.",
            view=view,
            ephemeral=True
        )
        await view.wait()

        if view.confirmed is True:
            remove_snipes_from_player(guild_id, player.id)
            remove_player(guild_id, player.id)
            await interaction.followup.send(f"{player.display_name} has been removed from the game.", ephemeral=True)
        elif view.confirmed is False:
            await interaction.followup.send("Player removal was cancelled.", ephemeral=True)
        else:
            await interaction.followup.send("Player removal timed out with no response.", ephemeral=True)

        

    @app_commands.command(name="resetgame", description="Reset the snipes and config of the game, all players remain in the game")
    async def reset_game(self, interaction: discord.Interaction):
        """
        Command to reset game

        Resets snipes database for current server
        Resets config
        Resets all users to base values
        """
        guild_id = interaction.guild.id
        config = ServerConfig(guild_id=guild_id)
        view = ConfirmDeleteView()
        await interaction.response.send_message(
            "Are you sure you want to reset the game? This action cannot be undone.",
            view=view,
            ephemeral=True
        )
        await view.wait()

        if view.confirmed is True:
            save_config(config)
            reset_snipes(guild_id)
            reset_players(guild_id)
            await interaction.followup.send("Game has been reset.", ephemeral=True)
        elif view.confirmed is False:
            await interaction.followup.send("Reset was cancelled.", ephemeral=True)
        else:
            await interaction.followup.send("Reset timed out with no response.", ephemeral=True)

    
    @app_commands.command(name="config", description="View or adjust the settings of the game")
    async def config(self, interaction: discord.Interaction, setting: Optional[Literal["points_per_snipe", "penalty_per_snipe", "achievements_enabled"]] = None, value: Optional[str] = None):
        guild_id = interaction.guild.id
        newConf = get_config(guild_id)
        if not setting:
            await interaction.response.send_message(
                f"**Current Config:**\n"
                f"- Points per snipe: `{newConf.points_per_snipe}`\n"
                f"- Penalty per snipe: `{newConf.penalty_per_snipe}`\n"
                f"- Achievements enabled: `{newConf.achievements_enabled}`",
                ephemeral=True
            )
            return

        match setting:
            case "points_per_snipe":
                newConf.points_per_snipe = float(value)
                save_config(newConf)
                await interaction.response.send_message(f"Points per snipe now set to {newConf.points_per_snipe}", ephemeral=True)
                return
            case "penalty_per_snipe":
                newConf.penalty_per_snipe = float(value)
                save_config(newConf)
                await interaction.response.send_message(f"Penalty per snipe now set to {newConf.penalty_per_snipe}", ephemeral=True)
                return
            case "achievements_enabled":
                if str(value) != "True" and str(value) != "False":
                    await interaction.response.send_message("Achievements_enabled must be `True` or `False`", ephemeral=True)
                    return
                newConf.achievements_enabled = str(value) == "True"
                save_config(newConf)
                await interaction.response.send_message(f"Achievements are now {"enabled" if newConf.achievements_enabled else "disabled"}", ephemeral=True)
                return

    
    
    
async def setup(bot):
    await bot.add_cog(Init(bot))
