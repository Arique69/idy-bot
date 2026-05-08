"""Persistent user data storage."""
from __future__ import annotations

import json
import os

DATA_FILE = "data.json"


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_user(data: dict, user_id: str) -> dict:
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "common_streak": 0,
            "collection": {},
            "legendary_count": 0,
            "mythic_count": 0,
        }
    user = data["users"][user_id]
    if isinstance(user.get("collection"), list):
        coll: dict[str, int] = {}
        for name in user["collection"]:
            coll[name] = coll.get(name, 0) + 1
        user["collection"] = coll
    return user
