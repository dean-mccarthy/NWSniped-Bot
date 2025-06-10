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
    print("player: ", player_id, "guild: ", guild_id)
    data = db.users.find_one({"guild_id": guild_id, "_id":player_id})
    print("data", data)
    if data:
        print("User: ", User.from_dict(data))
    return User.from_dict(data) if data else None

def save_player(player: User):
    db.users.replace_one(
        {"_id": player.user_id},
        player.to_dict(),
        upsert=True
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