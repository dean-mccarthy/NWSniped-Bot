import asyncio
from datetime import datetime, time
from zoneinfo import ZoneInfo
from discord import Interaction
import discord
from discord.app_commands import CheckFailure
from utils.util_db import *
from models import *
import random

PACIFIC = ZoneInfo("Canada/Pacific")

def pokedex(guild_id, sniper_data: User) -> bool:
    players = get_players_from_guild(guild_id)
    return (len(players) - 1) == sniper_data.targets

def kill_streak(guild_id, sniper_data: User) -> bool:
    return sniper_data.kill_streak == 4

def shut_down(guild_id, target_data: User) -> bool:
    return target_data.kill_streak >= 5

def revengeful(guild_id, sniper_data, target_data, s_snipes, t_snipes) -> bool:
    
    return

def love_triangle(guild_id, sniper_data, target_data,s_snipes, t_snipes) -> bool:
    return

def nothing_personnel(guild_id, sniper_data, target_data, s_snipes, t_snipes) -> bool:
    return


ACHV_FUNCS = [
    ("KILL_STREAK", kill_streak),
    ("SHUT_DOWN", shut_down),
    ("REVENGEFUL", revengeful),
    ("LOVE_TRIANGLE", love_triangle),
    ("NOTHING_PERSONNEL", nothing_personnel),
    ("COMPLETED_POKEDEX", pokedex)
]
async def check_achievements(bot: discord.Client, guild_id, sniper: discord.Member, target: discord.Member):
    sniper_id = sniper.id
    target_id = target.id
    sniper_data = get_player(guild_id, sniper_id)
    sniper_achv = sniper_data.achievements
    sniper_snipes = get_user_snipes(guild_id, sniper_id)
    target_snipes = get_user_snipes(guild_id, target_id)

    for achv, func in ACHV_FUNCS:
        if achv in sniper_achv:
            continue

        if func(guild_id, sniper_data, target_id, sniper_snipes, target_snipes):
            await send_achievement(bot, guild_id, sniper, AchievementName[achv])

    update_kill_streaks(guild_id, sniper_id, target_id)


async def send_achievement(bot: discord.Client, guild_id, player: discord.Member, achievement: AchievementName):
    guild_data = get_config(guild_id)
    channel = bot.get_channel(guild_data.channel)
    await channel.send(f"{player.mention} has been awarded **{achievement.value.name}**! Happy Hunting!")
    return
