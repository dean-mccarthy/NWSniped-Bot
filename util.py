import json
import os

CONFIG_DIR = os.path.join("data","config")
DATA_DIR = os.path.join("data", "game")

def load_data(guild_id):
    filename = get_filename(guild_id)
    if not os.path.exists(filename):
        return {"snipes": [], "users": {}}
    with open(filename, "r") as f:
        return json.load(f)

def save_data(guild_id, data):
    filename = get_filename(guild_id)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def get_filename(guild_id):
    #print("Finding file for guild: ", guild_id)
    filename = os.path.join(DATA_DIR, f"server_{guild_id}.json")
    #print("Found filename: ", filename)
    return filename

def save_config(guild_id, config):
    filename = get_config(guild_id)
    with open(filename, "w") as f:
        json.dump

def load_config(guild_id):
    filename = get_config(guild_id)
    if not os.path.exists(filename):
        config = {
            "points_per_snipe": 0.0,
            "penalty_per_snipe": 0.0,
            "achievements_enabled": False
        }
        return config
    with open(filename, "r") as f:
        return json.load(f)

def get_config(guild_id):
    filename = os.path.join(CONFIG_DIR, f"config_{guild_id}.json")
    #print("Found filename: ", filename)
    return filename

