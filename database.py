import json
import os

DATA_FILE = "bot_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"links": [], "secure_links": [], "files": [], "admins": [], "users": [], "announcements": []}
    with open(DATA_FILE, "r", encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
