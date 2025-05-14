import discord
from discord import app_commands
from discord.ext import commands
import os
from util import save_data, load_data, get_filename

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="pongs")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="initgame", description="Initialize or reset the snipe game")
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

        save_data(interaction.guild.id, {"snipes": [], "users": {}})
        await interaction.response.send_message("Game has been initialized!")

    @app_commands.command(name="addplayer", description="Register a player in the snipe game")
    @app_commands.describe(player="Select the player to add")
    async def add_player(self, interaction: discord.Interaction, player: discord.Member):
        guild_id = interaction.guild.id

        if not os.path.exists(get_filename(guild_id)):
            await interaction.response.send_message("Game is not initialized!")
            
        data = load_data(guild_id)
        user_id = str(player.id)

        if user_id in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is already registered.", ephemeral=True)
            return

        data["users"][user_id] = {"snipes_given": 0, "snipes_received": 0}
        save_data(guild_id, data)
        await interaction.response.send_message(f"{player.mention} has been added to the game!")
        return


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

        if target_id not in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is not in the game!.", ephemeral=True)
            return
        if target_id == str(interaction.user.id):
            await interaction.response.send_message("You can't snipe yourself!", ephemeral=True)
            return
        

async def setup(bot):
    await bot.add_cog(Basic(bot))

