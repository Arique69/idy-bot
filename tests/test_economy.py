import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import time
from data import get_user
from bot import get_daily_reward, can_claim_daily, get_duel_win_reward


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


def test_get_daily_reward_in_range():
    for _ in range(200):
        reward = get_daily_reward()
        assert 50 <= reward <= 100


def test_get_duel_win_reward_in_range():
    for _ in range(200):
        reward = get_duel_win_reward()
        assert 20 <= reward <= 40


def test_can_claim_daily_new_user():
    user = {"daily_last": 0}
    can_claim, remaining = can_claim_daily(user)
    assert can_claim is True
    assert remaining == 0.0


def test_can_claim_daily_just_claimed():
    user = {"daily_last": time.time()}
    can_claim, remaining = can_claim_daily(user)
    assert can_claim is False
    assert remaining > 86390


def test_can_claim_daily_expired():
    user = {"daily_last": time.time() - 86401}
    can_claim, remaining = can_claim_daily(user)
    assert can_claim is True
    assert remaining == 0.0
