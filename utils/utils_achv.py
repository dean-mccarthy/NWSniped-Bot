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
KS_CALLOUTS = {
    5: "on a **Killing Spree**",
    6: "on a **Rampage**",
    7: "**Unstoppable**",
    8: "**Dominating**",
    9: "***Godlike***",
    10: "***Legendary***"
}

# Check to see if the sniper has all players but themself
def pokedex(ctx: InGameAchvContext) -> bool:
    players = get_players_from_guild(ctx.guild_id)
    return (len(players) - 1) == len(ctx.sniper_data.targets)

# Check if killstreak is high enough
def kill_streak(ctx: InGameAchvContext) -> bool:
    return ctx.sniper_data.kill_streak == 4

# Check if enemy killstreak is high enough
def shut_down(ctx: InGameAchvContext) -> bool:
    return ctx.target_data.kill_streak >= 5

# Check if currSniper was a target of currTarget in the last week
def revengeful(ctx: InGameAchvContext) -> bool:
    t_last = filter_last_week(ctx.t_snipes)
    sniper_id = ctx.sniper_data.user_id
    return any(sniper_id == snipe.target_id for snipe in t_last)


def nothing_personnel(ctx: InGameAchvContext) -> bool:
    target_id = ctx.target_data.user_id
    total_snipes = sum(1 for s  in ctx.s_snipes if s.target_id == target_id)
    return total_snipes >= 3

async def love_triangle(ctx: InGameAchvContext, bot: discord.Client) -> bool:
    guild_id = ctx.guild_id
    sniper_id = ctx.sniper_data.user_id
    target_id = ctx.target_data.user_id
    s_snipes = ctx.s_snipes
    t_snipes = ctx.t_snipes

    s_last = filter_last_week(s_snipes)
    s_shots_recv = filter_last_week(get_user_shots_recv(guild_id, sniper_id))
    t_last = filter_last_week(t_snipes)
    t_shots_recv = filter_last_week(get_user_shots_recv(guild_id, target_id))

    match1 = triangle_solver(s_last, t_shots_recv) # Find players who have been shot by sniper and shot target
    match2 = triangle_solver(t_last, s_shots_recv) # Find players who have been shot by target and shot sniper

    matches = match1 + list(set(match2) - set(match1)) 
    achv = AchievementName("LOVE_TRIANGLE")
    for player_id in matches:
        player = bot.get_user(player_id)
        await send_achievement(bot, guild_id, player, achv)
        push_achv_user(player_id, guild_id, "LOVE_TRIANGLE")
    return

def triangle_solver(s_snipes, t_snipes):
    snipers = [s.sniper_id for s in t_snipes]
    targets = [t.target_id for t in s_snipes]
    matches = list(set(snipers) & set(targets))

    return matches



ACHV_FUNCS = [
    ("KILL_STREAK", kill_streak),
    ("SHUT_DOWN", shut_down),
    ("REVENGEFUL", revengeful),
    ("NOTHING_PERSONNEL", nothing_personnel),
    ("COMPLETED_POKEDEX", pokedex)
]
async def check_achievements(bot: discord.Client, guild_id, sniper: discord.Member, target: discord.Member):
    print("checking achvs")
    sniper_id = sniper.id
    target_id = target.id
    sniper_data = get_player(guild_id, sniper_id)
    target_data = get_player(guild_id, target_id)
    sniper_achv = sniper_data.achievements
    sniper_snipes = get_user_snipes(guild_id, sniper_id)
    target_snipes = get_user_snipes(guild_id, target_id)

    ctx = InGameAchvContext(guild_id, sniper_data, target_data, sniper_snipes, target_snipes)

    for achv, func in ACHV_FUNCS:
        if achv in sniper_achv:
            continue
        
        print("running", achv)
        if func(ctx):
            sniper_data.achievements.append(achv)
            await send_achievement(bot, guild_id, sniper, AchievementName[achv])
        else:
            print(f"{achv} not given")

    # update player achievements
    save_player(sniper_data, guild_id)

    # love triangle is intensive and a special case so should run last
    love_triangle(ctx, bot)



async def send_achievement(bot: discord.Client, guild_id, player: discord.Member, achievement: AchievementName):
    guild_data = get_config(guild_id)
    channel = bot.get_channel(guild_data.channel)
    print(f"sending {achievement} to {guild_data.channel}")
    await channel.send(f"{player.mention} has been awarded **{achievement.value.name}**! Happy Hunting!")
    return

def filter_last_week(snipes):
    last_week = (datetime.now(PACIFIC) - timedelta(days=7)).date()
    last_snipes = [ 
        s for s in snipes
        if datetime.fromisoformat(s.timestamp).date() >= last_week ] 
    
    return last_snipes


async def check_killspree(bot: discord.Client, guild_id, sniper: discord.Member, target: discord.Member):
    # print("checking ks")
    guild_data = get_config(guild_id)
    channel = bot.get_channel(guild_data.channel)
    # print("channel", channel)

    sniper_data = get_player(guild_id, sniper.id)
    target_data = get_player(guild_id, target.id)
    
    s_ks = sniper_data.kill_streak + 1
    if s_ks >= 5:
        s_ks = min(10, s_ks)
        await channel.send(f"{sniper.mention} is {KS_CALLOUTS.get(s_ks, "")}!")

    if target_data.kill_streak >= 5:
        await channel.send(f"{sniper.mention} has **SHUTDOWN** {target.mention}'s killing spree!")

    return

