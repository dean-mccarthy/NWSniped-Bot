import json
import os

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
    filename = f"data/server_{guild_id}.json"
    #print("Found filename: ", filename)
    return filename


