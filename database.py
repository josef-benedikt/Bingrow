import json
import os

SAVE_FILE = "accounts.json"

def load_all_accounts():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_account(username, password, stage_scores, current_stage):
    accounts = load_all_accounts()
    accounts[username] = {
        "password": password,
        "stage_scores": stage_scores,
        "current_stage": current_stage
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

def verify_login(username, password):
    accounts = load_all_accounts()
    if username in accounts and accounts[username]["password"] == password:
        return accounts[username]
    return None