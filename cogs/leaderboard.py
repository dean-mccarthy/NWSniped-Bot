import random
import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from util import *
from typing import Literal

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show the leaderboard")
    async def showleaderboard(self, interaction: discord.Interaction, sort_by: Literal["score", "snipes", "times_sniped"] = "score", sort_direction: Literal["Highest First", "Lowest First"] = "Highest First"):
        """
        Command called to generate current leaderboard in chat

        Returns:
            Message in chat with current leaderboard
        """
        print("Generating Leaderboard")
        guild_id = interaction.guild.id 

        data = load_data(guild_id)
        config = load_config(guild_id)

        rows = []
        if not data["users"].items():
            await interaction.response.send_message("No users in the game!")


        for user_id, user in data["users"].items():
            score = (user.snipes * config.points_per_snipe) - (user.times_sniped * config.penalty_per_snipe)
            member = interaction.guild.get_member(int(user_id))
            if member:
                name = member.display_name
            else:
                try:
                    user_obj = await self.bot.fetch_user(int(user_id))
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



async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))