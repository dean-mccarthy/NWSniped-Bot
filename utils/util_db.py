import discord
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import *
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set! Check your .env or environment variables.")
client = MongoClient(MONGO_URI)
db = client["sniped_bot"]


def get_config(guild_id):
    config = db.configs.find_one({"_id": guild_id})
    return ServerConfig.from_dict(config) if config else None

def save_config(config: ServerConfig):
    db.configs.replace_one(
        {"_id": config.guild_id},
        config.to_dict(),
        upsert=True
    )

def get_player(guild_id, player_id):
    data = db.users.find_one({"guild_id": guild_id, "user_id":player_id})
    # print("data", data)
    # if data:
    #     print("User: ", User.from_dict(data))
    return User.from_dict(data) if data else None

def save_player(player: User, guild_id):
    db.users.replace_one(
        {"user_id": player.user_id, "guild_id": guild_id},
        player.to_dict(),
        upsert=True
    )

def remove_player(guild_id, player_id):
    db.users.delete_one({"guild_id": guild_id, "user_id": player_id})

def get_players_from_guild(guild_id):
    data = db.users.find({"guild_id": guild_id})
    return [User.from_dict(user) for user in data]

def make_snipe(guild_id, sniper_id, target_id, channel_id):
    snipe = Snipe(guild_id, sniper_id, target_id, channel_id, False, datetime.now(ZoneInfo("Canada/Pacific")).isoformat())
    snipe_db = db.snipes.insert_one(snipe.to_dict())
    return snipe_db.inserted_id

def confirm_snipe(snipe_id):
    snipe_data = db.snipes.find_one({"_id": ObjectId(snipe_id)})
    if not snipe_data or snipe_data.get("confirmed"):
        return False
    snipe = Snipe.from_dict(snipe_data)
    guild_id = snipe.guild_id
    sniper_id = snipe.sniper_id
    target_id = snipe.target_id

    sniper = get_player(guild_id, sniper_id)
    target = get_player(guild_id, target_id)
    
    # update sniper
    sniper.snipes += 1
    if target_id not in sniper.targets: 
        sniper.targets.append(target_id)
    save_player(sniper, guild_id)

    # update target
    target.times_sniped += 1
    save_player(target, guild_id)
    
    # update snipe confirmation status
    db.snipes.update_one(
        {"_id": ObjectId(snipe_id)}, 
        {"$set": {"confirmed": True}}
        ) 
    
def update_kill_streaks(guild_id, sniper_id, target_id):
    sniper = get_player(guild_id, sniper_id)
    target = get_player(guild_id, target_id)

    sniper.kill_streak += 1
    save_player(sniper, guild_id)

    target.kill_streak = 0
    save_player(target, guild_id)

def remove_snipe_by_id(snipe_id):
    db.snipes.delete_one({"_id": ObjectId(snipe_id)})

def get_snipe_by_id(snipe_id):
    snipe_data = db.snipes.find_one({"_id":snipe_id})
    return Snipe.from_dict(snipe_data)

# Returns all snipes where the player is the sniper
def get_user_snipes(guild_id, player_id):
    snipe_data = db.snipes.find({
        "guild_id": guild_id,
        "sniper_id": player_id
    })
    return [Snipe.from_dict(snipe) for snipe in snipe_data]

# Returns all snipes where the player is the target
def get_user_shots_recv(guild_id, player_id):
    snipe_data = db.snipes.find({
        "guild_id": guild_id,
        "target_id": player_id
    })
    return [Snipe.from_dict(snipe) for snipe in snipe_data]

def get_unconfirmed_snipes():
    snipes = db.snipes.find({"confirmed": False})
    return [(snipe["_id"], Snipe.from_dict(snipe)) for snipe in snipes]

# Returns all snipes from a guild
def get_snipes_from_guild(guild_id, limit):
    data = db.snipes.find({"guild_id": guild_id, "confirmed": True}).sort("timestamp", -1).limit(limit)
    count = db.snipes.count_documents({"guild_id": guild_id, "confirmed": True})
    return ([Snipe.from_dict(snipe) for snipe in reversed(list(data))], count)

def remove_snipe(guild_id, index) -> bool:
    snipes = list(db.snipes.find({"guild_id": guild_id}).sort("timestamp", 1))
    if index < 1 or index > len(snipes):
        return False
    del_data = snipes[index - 1]
    del_snipe = Snipe.from_dict(del_data)

    db.users.update_one( # update sniper
        {"guild_id": guild_id, "user_id": del_snipe.sniper_id},
        {"$inc": {"snipes": -1}}
        )
    db.users.update_one( # update target
        {"guild_id": guild_id, "user_id": del_snipe.target_id},
        {"$inc": {"times_sniped": -1}}
        )
    

    remove_snipe_by_id(del_data["_id"])
    return True

def remove_snipes_from_player(guild_id, player_id):
    snipes_against = [Snipe.from_dict(snipe) for snipe in db.snipes.find({"guild_id": guild_id, "target_id": player_id, "confirmed": True})]

    for snipe in snipes_against:
        db.users.update_one( # update target
        {"guild_id": guild_id, "user_id": snipe.sniper_id},
        {"$inc": {"snipes": -1}}
        )

    snipes_by_player = [Snipe.from_dict(snipe) for snipe in db.snipes.find({"guild_id": guild_id, "sniper_id": player_id, "confirmed": True})]

    for snipe in snipes_by_player:
        db.users.update_one( # update target
        {"guild_id": guild_id, "user_id": snipe.target_id},
        {"$inc": {"times_sniped": -1}}
        )

    db.snipes.delete_many({
        "guild_id": guild_id,
        "$or": [{"target_id": player_id}, {"sniper_id": player_id}]
    })


def reset_snipes(guild_id):
    db.snipes.delete_many({"guild_id": guild_id})

def reset_players(guild_id):
    db.users.update_many(
        {"guild_id": guild_id},
        {
            "$set": {
                "snipes": 0,
                "times_sniped": 0,
                "killstreak": 0,
                "achievements": [],
                "targets": [],
            }
        }
    )

    

def add_player_helper(guild_id: int, player: discord.Member):
    
    user_id = player.id
    if get_player(guild_id, user_id):
        return (f"{player.display_name} is already registered.", True)

    newPlayer = User(int(player.id), int(guild_id))
    save_player(newPlayer, guild_id)

    return (f"{player.mention} has been added to the game!", False)

async def get_name(bot: discord.Client, guild_id: int, player_id: int) -> str:
    # print("finding name")
    guild  = await bot.fetch_guild(guild_id)
    # print(guild)
    member = await guild.fetch_member(player_id)
    # print(member, member.nick, member.display_name)
    if member:
        if member.nick:
            return member.nick
        else: 
            return member.display_name
    try:
        user_obj = await bot.fetch_user(player_id)
        return user_obj.name  # fallback to username - not nickname
    except:
        return "Unknown"

                