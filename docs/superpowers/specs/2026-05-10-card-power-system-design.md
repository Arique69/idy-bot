# Card Power System Design

**Date:** 2026-05-10

## Overview

Add a `power` stat to each card that makes `/duel` more interesting. Higher-power cards are more likely to win, but upsets are possible via weighted random.

## Card Power Values

Each card in `config.py` gets a new `"power"` integer field. Default values by rarity:

| Rarity   | Default Power |
|----------|--------------|
| Common   | 100          |
| Rare     | 250          |
| Epic     | 450          |
| Legendary| 700          |
| Mythic   | 900          |

All values are manually adjustable per card after initial scaffolding.

## Duel Logic

### Card Selection
Duel pulls a random card from each player's collection instead of the full card pool.

- If either player has an empty collection, the bot replies ephemerally: `"Kamu/lawan belum punya kartu! Ketik 'idy' buat dapet kartu dulu."`
- Card is selected by picking a random key from `user["collection"]`, then looking it up in `CARDS`.

### Win Probability Formula (Option A — Direct Ratio)
```
win_chance_a = power_a / (power_a + power_b)
roll = random.random()
winner = A if roll < win_chance_a else B
```

No draws. If both cards have equal power, the odds are 50/50.

### Duel Embed
Shows both cards with power and the win probability:

```
⚔️ DUEL KARTU!

[User A]                VS            [User B]
🟣 Epic Card Name              ⚪ Common Card Name
⚡ 450                                  ⚡ 100
Peluang menang: 81.8% vs 18.2%

🏆 [User A] menang!
```

## Files Changed

| File | Change |
|------|--------|
| `config.py` | Add `"power"` field to every card entry |
| `bot.py` | Replace `pull_card_simple()` with `get_random_collection_card()`, update duel win logic and embed |

## Out of Scope

- Power is not shown on pull embeds or `/kartu` preview
- Power does not affect collection or trade mechanics
- `duel_draws` field in user data is kept as-is (not removed)
