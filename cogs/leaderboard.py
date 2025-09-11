import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import check
import os
from dotenv import load_dotenv
from utils.util_db import *
from utils.utils_checks import *
from typing import Literal
from datetime import datetime
from views import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show the leaderboard")
    @check(check_initialized)
    async def showleaderboard(self, interaction: discord.Interaction, sort_by: Literal["name", "score", "snipes", "times_sniped"] = "score", sort_direction: Literal["Highest First", "Lowest First"] = "Highest First"):
        """
        Command called to generate current leaderboard in chat

        Returns:
            Message in chat with current leaderboard
        """
        guild_id = interaction.guild.id 

        players = get_players_from_guild(guild_id)
        config = get_config(guild_id)

        rows = []
        if not players:
            await interaction.response.send_message("No users in the game!")
            return

        # print("Players:", players)

        for user in players:
            score = (user.snipes * config.points_per_snipe) - (user.times_sniped * config.penalty_per_snipe)
            name = await get_name(self.bot, guild_id, user.user_id)
            rows.append((name, user.snipes, user.times_sniped, score))
        # print("rows: ", rows)

        sort_index = {"name": 0, "snipes": 1, "times_sniped": 2, "score": 3}[sort_by]
        rows.sort(key=lambda x: x[sort_index], reverse= sort_direction == "Highest First")

        table = []
        header = f"{'Name':<20} {'Snipes':>6} {'Times sniped':>13} {'Score':>6}"
        table.append(header)
        # print(table)
        table.append("-" * len(header))
        for name, snipes, sniped, score in rows:
            table.append(f"{name:<20} {snipes:>6.0f} {sniped:>13.0f} {score:>6.1f}")
        # print(table)
        output = "```text\n" + "\n".join(table) + "\n```"
        await interaction.response.send_message(output)

    @app_commands.command(name="listplayers", description="Lists all registered players")
    @check(check_initialized)
    async def list_players(self, interaction: discord.Interaction):
        """
        Command to list all players

        Returns:
            List of all players in codeblock format
        """

        guild_id = interaction.guild.id 

        data = get_players_from_guild(guild_id)

        rows = []
        if not data:
            await interaction.response.send_message("No users in the game!")
            return

        for user in data:
            name = await get_name(self.bot, guild_id, user.user_id)
            rows.append(name)

        rows.sort()
        output = "```PLAYER NAME:\n" + "\n".join(rows) + "\n```"
        await interaction.response.send_message(output)


    @app_commands.command(name="listsnipes", description="Lists snipes")
    @app_commands.describe(number_of_snipes="Select the number of snipes you wish to view")
    @check(check_initialized)
    async def list_snipes(self, interaction: discord.Interaction, number_of_snipes: int = 10):
        """
        Command to list snipes

        Args:
            number_of_snipes: number of snipes to show, counting from the most recent snipe

        Returns:
            List of snipes in codeblock format
        """

        guild_id = interaction.guild.id 

        data = get_snipes_from_guild(guild_id)
        snipes = data[0]
        snipe_count = data[1]

        rows = []
        if not snipes:
            await interaction.response.send_message("No snipes in the game!")
            return
        
        number_of_snipes = min(number_of_snipes, len(snipes))

        for i in range (number_of_snipes):
            index = snipe_count - number_of_snipes + i
            snipe: Snipe = snipes[i]
            sniper = await get_name(self.bot, guild_id, snipe.sniper_id)
            target = await get_name(self.bot, guild_id, snipe.target_id)
            rows.append((index, sniper, target, snipe.timestamp))
        print("rows: ", rows)

        table = []
        header = f"{'Snipe':<6} {'Sniper':>20} {'Target':>20} {'Time':>20}"
        table.append(header)
        table.append("-" * len(header))
        for index, sniper, target, timestamp in rows:
            table.append(f"{index:<6} {sniper:>20} {target:>20} {timestamp:>20}")
        print(table)
        output = "```SNIPES:\n" + "\n".join(table) + "\n```"
        await interaction.response.send_message(output)


    @app_commands.command(name="listsnipes", description="Lists snipes")
    @app_commands.describe(number_of_snipes="Select the number of snipes you wish to view")
    @check(check_initialized)
    async def list_snipes(self, interaction: discord.Interaction, number_of_snipes: int = 10):
        """
        Command to list snipes

        Args:
            number_of_snipes: number of snipes to show, counting from the most recent snipe

        Returns:
            List of snipes in codeblock format
        """
        # print("Listing Snipes")
        guild_id = interaction.guild.id 

        snipes, snipe_count = get_snipes_from_guild(guild_id, number_of_snipes)
        # print(snipes)
        rows = []
        if not snipes:
            await interaction.response.send_message("No snipes in the game!")
            return
        number_of_snipes = min(number_of_snipes, len(snipes))
        
        for i in range (1, number_of_snipes+1):
            index = snipe_count - number_of_snipes + i
            snipe: Snipe = snipes[i-1]
            sniper = await get_name(self.bot, guild_id, snipe.sniper_id)
            target = await get_name(self.bot, guild_id, snipe.target_id)
            time = datetime.fromisoformat(snipe.timestamp).strftime("%b %d %I:%M %p")
            rows.append((index, sniper, target, time))
        # print("rows: ", rows)

        table = []
        header = f"{'Snipe':<6} {'Sniper':>20} {'Target':>20} {'Time':>20}"
        table.append(header)
        table.append("-" * len(header))
        for index, sniper, target, timestamp in rows:
            table.append(f"{index:<6} {sniper:>20} {target:>20} {timestamp:>20}")
        # print(table)
        output = "```SNIPES:\n" + "\n".join(table) + "\n```"
        await interaction.response.send_message(output)

    @app_commands.command(name="deletesnipe", description="Deletes the selected snipe")
    @app_commands.describe(snipe_number="Select the snipe you want to remove")
    @check(check_perms)
    @check(check_initialized)
    async def delete_snipe(self, interaction: discord.Interaction, snipe_number: int):
        guild_id = interaction.guild.id
        result = remove_snipe(guild_id, snipe_number)
        if not result:
            await interaction.response.send_message("Please select a valid snipe", ephemeral=True)
            return
        await interaction.response.send_message(f"Snipe {snipe_number} successfully deleted!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))