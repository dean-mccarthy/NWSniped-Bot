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

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="View or adjust the settings of the game")
    @app_commands.describe(setting="Setting to change", value="Value of selected setting")
    @check(check_perms)
    @check(check_initialized)
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
            
    @app_commands.command(name="safetime", description="Add, or view safetimes")
    @app_commands.describe(day="Day of the week", start_time="Start time (HH:MM)", end_time="End time (HH:MM)")
    @check(check_perms)
    @check(check_initialized)
    async def safetime(self, interaction: discord.Interaction, day: Optional[Literal["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]] = None, start_time: Optional[str] = None, end_time: Optional[str] = None):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        guild_id = interaction.guild.id
        newConf = get_config(guild_id)
        if not day:
            times = newConf.safe_times
            if not times:
                await interaction.response.send_message("No safetimes currently set!", ephemeral=True)
                return
            
            rows = []
            index = 1
            sorted_times = sorted(times, key=lambda s: (s.day, s.start_time))

            for safetime in sorted_times:
                rows.append((index, days[safetime.day], safetime.start_time, safetime.end_time))
                index += 1
                
            table = []
            header = f"{'#':<3}{'Day':<10} {'Start Time':>10} {'End Time':>10}"
            table.append(header)
            table.append("-" * len(header))
            for num, day, start, end in rows:
                table.append(f"{num:<3} {day:<10} {start.strftime('%H:%M'):>10} {end.strftime('%H:%M'):>10}")
            output = "```SAFETIMES:\n" + "\n".join(table) + "\n```"
            await interaction.response.send_message(output, ephemeral=True)
            return


        if not (start_time and end_time):
            await interaction.response.send_message("Safetime must have a start and end time!", ephemeral=True)
            return
        start = await validate_time_format(start_time)
        end = await validate_time_format(end_time)
        if not (start and end):
            await interaction.response.send_message("Start and end times must be in 24h HH:MM format - e.g. 17:45, 21:45", ephemeral=True)
            return

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dayIndex = days.index(day)
        newSafeTime = SafeTime(dayIndex, start, end)
        newConf.safe_times.append(newSafeTime)
        save_config(newConf)
        await interaction.response.send_message("Safetime successfully added!", ephemeral=True)


    @app_commands.command(name="removesafetime", description="Remove safetime")
    @app_commands.describe(safetime="Index of safetime to remove")
    @check(check_perms)
    @check(check_initialized)
    async def remove_safetime(self, interaction: discord.Interaction, safetime: int):
        guild_id = interaction.guild.id
        config = get_config(guild_id)
        times = sorted(config.safe_times, key=lambda s: (s.day, s.start_time))
        if safetime < 1 or safetime > len(times):
            await interaction.response.send_message("Please select a valid safetime", ephemeral=True)
            return 
        
        del times[safetime - 1]

        config.safe_times = times
        save_config(config)
        await interaction.response.send_message("Safetime successfully removed!", ephemeral=True)
        return
    
    @app_commands.command(name="rules", description="Displays the rules of the game")
    @check(check_initialized)
    async def rules(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        config = get_config(guild_id)

        rules_text = None
        readme_path = os.path.join(os.getcwd(), "Rules.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                self.rules_text = f.read()
        else:
            self.rules_text = "Rules file not found."

        text = rules_text[:3500]

        text += (
                "\n\n**Current Scoring:**\n"
                f"- Points per snipe: `{config.points_per_snipe}`\n"
                f"- Penalty per snipe: `{config.penalty_per_snipe}`"
            )
        
        embed = discord.Embed(
            title="Game Rules",
            description=text[:4000],
            color=discord.Color.gold()
        )






    
async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))
    