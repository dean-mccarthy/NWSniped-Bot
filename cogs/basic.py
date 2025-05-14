import discord
from discord import app_commands
from discord.ext import commands
import os
from util import save_data, load_data


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="pongs")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="initgame", description="Initialize or reset the snipe game")
    async def init_game(self, interaction: discord.Interaction):
        if os.path.exists("sniped.json"):
            data = load_data()
            if data.get("users") or data.get("snipes"):
                await interaction.response.send_message("Game already exists!", ephemeral=True)
                return

        save_data({"snipes": [], "users": {}})
        await interaction.response.send_message("Game has been initialized!", ephemeral=True)

    @app_commands.command(name="addplayer", description="Register a player in the snipe game")
    @app_commands.describe(player="Select the player to add")
    async def add_player(self, interaction: discord.Interaction, player: discord.Member):
        data = load_data()
        user_id = str(player.id)

        if user_id in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is already registered.", ephemeral=True)
            return

        data["users"][user_id] = {"snipes_given": 0, "snipes_received": 0}
        save_data(data)
        await interaction.response.send_message(f"{player.display_name} has been added to the game!", ephemeral=True)


    @app_commands.command(name="snipe", description="Snipe a player!")
    @app_commands.describe(player="Select the player to snipe")
    async def snipe(self, interaction: discord.Interaction, player: discord.Member):
        data = load_data()
        target_id = str(player.id)

        if target_id not in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is not in the game!.", ephemeral=True)
            return
        if target_id == interaction.user.id:
            await interaction.response.send_message("You can't snipe yourself!", ephemeral=True)
            return
        

async def setup(bot):
    await bot.add_cog(Basic(bot))
