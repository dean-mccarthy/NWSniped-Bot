import discord
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import *
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
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
    data = db.users.find_one({"guild_id": guild_id, "_id":player_id})
    # print("data", data)
    # if data:
    #     print("User: ", User.from_dict(data))
    return User.from_dict(data) if data else None

def save_player(player: User):
    db.users.replace_one(
        {"_id": player.user_id},
        player.to_dict(),
        upsert=True
    )

def remove_player(guild_id, player_id):
    db.users.remove({"guild_id": guild_id, "_id": player_id})

def get_players_from_guild(guild_id):
    data = db.users.find({"guild_id": guild_id})
    return [User.from_dict(user) for user in data]

def update_snipes(guild_id, sniper_id, target_id, increment: bool):
    value = 1.0 if increment else -1.0 # used for incrementing or decrementing snipes
    print(value)
    db.users.update_one( # update sniper
        {"guild_id": guild_id, "_id": sniper_id},
        {"$inc": {"snipes": value}}
        )
    db.users.update_one( # update target
        {"guild_id": guild_id, "_id": target_id},
        {"$inc": {"times_sniped": value}}
        )
    
    if increment: 
        snipe = Snipe(guild_id, sniper_id, target_id)
        db.snipes.insert_one(snipe.to_dict()) # add snipe to collection


def get_snipes_from_guild(guild_id, limit):
    data = db.snipes.find({"guild_id": guild_id}).sort("timestamp", -1).limit(limit)
    count = db.snipes.count_documents({"guild_id": guild_id})
    return ([Snipe.from_dict(snipe) for snipe in reversed(list(data))], count)

def remove_snipe(guild_id, index) -> bool:
    snipes = list(db.snipes.find({"guild_id": guild_id}).sort("timestamp", 1))
    if index < 1 or index > len(snipes):
        return False
    del_snipe = snipes[index - 1]
    target_id = del_snipe["target_id"]
    sniper_id = del_snipe["sniper_id"]
    update_snipes(guild_id, sniper_id, target_id, False)

    db.snipes.delete_one({"_id": del_snipe["_id"]})
    return True


def reset_snipes(guild_id):
    db.snipes.remove({"guild_id": guild_id})

def reset_players(guild_id):
    db.users.update_many(
        {"guild_id": str(guild_id)},
        {
            "$set": {
                "snipes": 0.0,
                "times_sniped": 0.0,
                "achievements": []
            }
        }
    )

    

def add_player_helper(guild_id: int, player: discord.Member):
    if not get_config(guild_id):
        return ("Game is not initialized!", False)
        
    user_id = player.id
    if get_player(guild_id, user_id):
        return (f"{player.display_name} is already registered.", True)

    newPlayer = User(int(player.id), int(guild_id))
    save_player(newPlayer)

    return (f"{player.mention} has been added to the game!", False)

async def get_name(interaction: discord.Interaction, player_id: int) -> str:
    guild = interaction.guild
    member = guild.get_member(player_id)
    if member:
        return member.display_name
    try:
        user_obj = await interaction.client.fetch_user(player_id)
        return user_obj.name  # fallback to username (not nickname)
    except:
        return "Unknown"

                