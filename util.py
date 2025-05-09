import json
import os

DATA_FILE = "snipes.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"snipes": [], "users": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
