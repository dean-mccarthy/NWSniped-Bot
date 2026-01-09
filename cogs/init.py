import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import check
import os
from models import *
from dotenv import load_dotenv
from utils.util_db import *
from utils.utils_checks import *
from typing import Literal, Optional
from views import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Init(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="tongs")
    async def ping(self, interaction: discord.Interaction):
        file = discord.File("tong.jpg", filename="tong.jpg")
        await interaction.response.send_message(
        content="All hail father Reese, founder of SneakCore",
        file=file
    )

    @app_commands.command(name="help", description="List all available commands")
    async def help(self, interaction:discord.Interaction):
        embed = discord.Embed(title="Sniped Bot Help", description="", color=discord.Color.purple())
        embed.add_field(name="Use `/startgame` to get the game started!", value="", inline=False)
        embed.add_field(name="Here are all of my commands:", value="", inline=False)

        commands = sorted(self.bot.tree.get_commands(), key=lambda cmd:cmd.name)

        for command in commands:
            embed.add_field(
                name=f"/{command.name}",
                value=command.description or "No description provided.",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="startgame", description="Start the snipe game in this channel")
    @check(check_perms)
    async def start_game(self, interaction: discord.Interaction):
        """
        Command to initialize game

        Initializes mongo file for current server if one does not exist already
        """
        #print("Attempting to init game")
        guild_id = interaction.guild.id
        check_config = get_config(guild_id)
        if check_config:
            await interaction.response.send_message("Game already exists!", ephemeral=True)
            return
        
        config = ServerConfig(guild_id=guild_id, channel=interaction.channel_id)
        save_config(config)

        await interaction.response.send_message("Game has begun! Good Luck and Good Hunting!")

    @app_commands.command(name="setchannel", description="Set the game to play in the current channel")
    @check(check_perms)
    @check(check_initialized)
    async def set_channel(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id
        config = get_config(guild_id)
        config.channel = interaction.channel_id
        save_config(config)

        await interaction.response.send_message("Game channel has been changed to *this* channel")

        
    @app_commands.command(name="addplayer", description="Register a player in the snipe game")
    @app_commands.describe(player="Select the player to add")
    @check(check_perms)
    @check(check_initialized)
    async def add_player(self, interaction: discord.Interaction, player: discord.Member):
        guild_id = interaction.guild.id

        result = add_player_helper(guild_id, player)
        await interaction.response.send_message(result[0], ephemeral=result[1])
        return
    
    @app_commands.command(name="joingame", description="Register yourself in the snipe game")
    @check(check_initialized)
    async def join_game(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id

        result = add_player_helper(guild_id, interaction.user)
        await interaction.response.send_message(result[0], ephemeral=result[1])
        return
    
    @app_commands.command(name="removeplayer", description="Remove a player from the game, also removes all snipes related to player")
    @app_commands.describe(player="Select the player to remove")
    @check(check_perms)
    @check(check_initialized)
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
    @check(check_perms)
    @check(check_initialized)
    async def reset_game(self, interaction: discord.Interaction):
        """
        Command to reset game

        Resets snipes database for current server
        Resets config
        Resets all users to base values
        """
        guild_id = interaction.guild.id
        config = ServerConfig(guild_id=guild_id, channel=interaction.channel_id)
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


    
    
async def setup(bot):
    await bot.add_cog(Init(bot))
