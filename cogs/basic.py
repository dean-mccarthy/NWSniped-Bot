import discord
from discord import app_commands
from discord.ext import commands
from util import save_data, load_data


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
        save_data(interaction.guild.id, {"snipes": [], "users": {}})
        await interaction.response.send_message("Game has been initialized!")

    @app_commands.command(name="addplayer", description="Register a player in the snipe game")
    @app_commands.describe(player="Select the player to add")
    async def add_player(self, interaction: discord.Interaction, player: discord.Member):
        data = load_data(interaction.guild.id)
        user_id = str(player.id)

        if user_id in data["users"]:
            await interaction.response.send_message(f"{player.display_name} is already registered.", ephemeral=True)
            return

        data["users"][user_id] = {"snipes_given": 0, "snipes_received": 0}
        save_data(interaction.guild.id, data)
        await interaction.response.send_message(f"{player.display_name} has been added to the game!", ephemeral=True)



    @app_commands.command(name="Snipe", description="Snipe a player")
    @app_commands.describe(player="Select the player to snipe")
    async def snipe_player(self, interaction: discord.Interaction, player: discord.Member):
        """
        Command called when player wishes to submit a snipe of another player
        Game rules indicate an image must precede or follow this command featuring the snipe

        Args:
            player (discord.Member): The target being sniped

        Returns:
            Ephemeral message to the target requesting confirmation of snipe
        """


        

async def setup(bot):
    await bot.add_cog(Basic(bot))
