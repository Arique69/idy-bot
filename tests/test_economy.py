import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data import get_user


def test_daily_last_defaults_to_zero_new_user():
    data = {"users": {}}
    user = get_user(data, "999")
    assert user["daily_last"] == 0


def test_daily_last_defaults_to_zero_existing_user_without_field():
    data = {
        "users": {
            "999": {
                "common_streak": 0,
                "collection": {},
                "legendary_count": 0,
                "mythic_count": 0,
                "duel_wins": 0,
                "duel_losses": 0,
                "duel_draws": 0,
                "coins": 50,
            }
        }
    }
    user = get_user(data, "999")
    assert user["daily_last"] == 0
