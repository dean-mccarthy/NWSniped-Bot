import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from models import User, ServerConfig

CONFIG_DIR = os.path.join("data","config")
DATA_DIR = os.path.join("data", "game")

def load_data(guild_id):
    filename = get_filename(guild_id)
    if not os.path.exists(filename):
        return {"snipes": [], "users": {}}
    with open(filename, "r") as f:
        data = json.load(f)
        data["users"] = {k: User.from_dict(v) for k, v in data["users"].items()}
        return data

def save_data(guild_id, data):
    filename = get_filename(guild_id)
    json_data = {
        "snipes": data.get("snipes", []),
        "users": {k: v.to_dict() for k, v in data["users"].items()}
    }
    with open(filename, "w") as f:
        json.dump(json_data, f, indent=2)

def get_filename(guild_id):
    #print("Finding file for guild: ", guild_id)
    filename = os.path.join(DATA_DIR, f"server_{guild_id}.json")
    #print("Found filename: ", filename)
    return filename

def save_config(guild_id, config):
    filename = get_config(guild_id)
    with open(filename, "w") as f:
        json.dump(config.to_dict(), f, indent=2)

def load_config(guild_id):
    filename = get_config(guild_id)
    if not os.path.exists(filename):
        return ServerConfig()
    
    with open(filename, "r") as f:
        return ServerConfig.from_dict(json.load(f))

def get_config(guild_id):
    filename = os.path.join(CONFIG_DIR, f"config_{guild_id}.json")
    #print("Found filename: ", filename)
    return filename

def add_player_helper(guild_id: int, player: discord.Member):
    if not os.path.exists(get_filename(guild_id)):
        return ("Game is not initialized!", False)
        
    data = load_data(guild_id)
    user_id = str(player.id)

    if user_id in data["users"]:
        return (f"{player.display_name} is already registered.", True)

    data["users"][user_id] = User()
    save_data(guild_id, data)

    return (f"{player.mention} has been added to the game!", False)

