import random
import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from util_db import *
from typing import Literal

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show the leaderboard")
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

        print("Players:", players)

        for user in players:
            score = (user.snipes * config.points_per_snipe) - (user.times_sniped * config.penalty_per_snipe)
            member = interaction.guild.get_member(int(user.user_id))
            if member:
                name = member.display_name
            else:
                try:
                    user_obj = await self.bot.fetch_user(user.user_id)
                    name = user_obj.name  # fallback to username (not nickname)
                except:
                    name = "Unknown"

            rows.append((name, user.snipes, user.times_sniped, score))
        print("rows: ", rows)

        sort_index = {"name": 0, "snipes": 1, "times_sniped": 2, "score": 3}[sort_by]
        rows.sort(key=lambda x: x[sort_index], reverse= sort_direction == "Highest First")

        table = []
        header = f"{'Name':<20} {'Snipes':>6} {'Times sniped':>13} {'Score':>6}"
        table.append(header)
        print(table)
        table.append("-" * len(header))
        for name, snipes, sniped, score in rows:
            table.append(f"{name:<20} {snipes:>6.0f} {sniped:>13.0f} {score:>6.1f}")
        print(table)
        output = "```text\n" + "\n".join(table) + "\n```"
        await interaction.response.send_message(output)

    @app_commands.command(name="listplayers", description="Lists all registered players")
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

        for user in data:
            member = interaction.guild.get_member(int(user.user_id))
            if member:
                name = member.display_name
            else:
                try:
                    user_obj = await self.bot.fetch_user(int(user.user_id))
                    name = user_obj.name  # fallback to username (not nickname)
                except:
                    name = "Unknown"
            rows.append(name)

        rows.sort()
        output = "```PLAYER NAME:\n" + "\n".join(rows) + "\n```"
        await interaction.response.send_message(output)



async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))