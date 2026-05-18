import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot import compute_win_chance

def test_same_rarity_same_atk_is_50_50():
    card = {"rarity": "rare", "atk": 40, "skill": None}
    assert compute_win_chance(card, card) == 0.5

def test_same_rarity_higher_atk_wins_more():
    high = {"rarity": "rare", "atk": 50, "skill": None}
    low  = {"rarity": "rare", "atk": 25, "skill": None}
    chance = compute_win_chance(high, low)
    assert chance > 0.5
    assert abs(chance - 0.525) < 0.001  # (50-25)/1000 = 0.025 bonus

def test_skill_bonus_increases_chance():
    base  = {"rarity": "epic", "atk": 60, "skill": None}
    skill = {"rarity": "epic", "atk": 60, "skill": {"name": "X", "desc": "Y", "bonus": 0.09}}
    assert compute_win_chance(skill, base) > compute_win_chance(base, base)
    assert abs(compute_win_chance(skill, base) - 0.59) < 0.001

def test_opponent_skill_reduces_chance():
    no_skill   = {"rarity": "epic", "atk": 60, "skill": None}
    with_skill = {"rarity": "epic", "atk": 60, "skill": {"name": "X", "desc": "Y", "bonus": 0.09}}
    chance = compute_win_chance(no_skill, with_skill)
    assert chance < 0.5
    assert abs(chance - 0.41) < 0.001  # 0.5 + 0 - 0.09 = 0.41

def test_result_clamped_between_005_and_095():
    mythic  = {"rarity": "mythic",  "atk": 110, "skill": {"name": "X", "desc": "Y", "bonus": 0.22}}
    common  = {"rarity": "common",  "atk": 10,  "skill": None}
    assert compute_win_chance(mythic, common) == 0.95
    assert compute_win_chance(common, mythic) == 0.05
