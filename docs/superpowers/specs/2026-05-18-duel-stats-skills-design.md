# Duel Stats & Skills System

**Date:** 2026-05-18  
**Status:** Approved

## Problem

The duel system is too random — outcome is driven purely by rarity-based probability rolls, so individual cards feel interchangeable. Two legendaries play identically.

## Solution

Layer ATK stats and passive skills on top of the existing rarity-probability system (Option A). Keep the "underdog can still win" feel, but make individual cards matter.

---

## Architecture

No new files. All changes are in `config.py` (card definitions) and `bot.py` (duel logic + embed).

---

## Card Stats

Each card in `config.py` gets an `"atk"` field — a deterministic integer seeded from `hash(name)` within the rarity's ATK range. Same card always has the same ATK; no storage needed.

| Rarity | ATK Range |
|--------|-----------|
| common | 10–30 |
| rare | 25–50 |
| epic | 45–75 |
| legendary | 65–95 |
| mythic | 85–110 |
| special | 9999 (fixed) |

---

## Skills

Each epic+ card gets a `"skill"` field. Common and rare cards have `"skill": None`.

Skill format:
```python
{"name": "...", "desc": "...", "bonus": 0.XX}
```

`bonus` is a flat addition to win probability. Skills are passive — always active, no activation needed.

### Epic Skills

| Card | Skill Name | Description | Bonus |
|------|-----------|-------------|-------|
| Sodara | Koneksi Sodara | Family pulls strings behind the scenes | +8% |
| Kenapa? | Pertanyaan Filosofis | Opponent is too confused to focus | +6% |
| Rusdi Balon | Melayang | Floats above the conflict | +7% |
| Mahkota Mu King | Aura Raja | Royal presence intimidates opponent | +10% |
| Owo Swag | Too Swag | Opponent can't help but be impressed | +8% |
| Menggugah Selera | Lapar Duluan | Makes opponent hungry, loses focus | +7% |
| Solo Baca Buku | Galaxy Brain | Big brain moves | +9% |
| Ape pula bodoh nih | Dismissal Aura | So annoying opponent ragequits early | +6% |
| Tertawa Tapi Teluka | Trauma Tertawa | Hides pain with laughter, catches opponent off guard | +8% |
| Terompet Pemanggil Pasukan | Backup Datang! | Calls the whole squad | +12% |
| Owo Sigma | Sigma Grindset | Never stops grinding | +9% |

### Legendary Skills

| Card | Skill Name | Description | Bonus |
|------|-----------|-------------|-------|
| Toyota Supra 2000HP BRAkTAKTAK | 2000HP Drift | Goes BRAKTAKTAK and overtakes everything | +15% |
| Merah | Murka Merah | Rage mode activated | +13% |
| Tirai Misterius | Tirai Terbuka | Nobody knows what's behind. Truly unpredictable | +12% |
| Solo Swag | Solo Mode ON | Locked in, impossible to distract | +14% |
| Rusdi nah ini | Udah Nah Ini | When Rusdi says this, it's over | +13% |
| Rusdi Informasi Palsu | Hoaks Tersebar | Opponent believes fake news and panics | +11% |
| Dimas Ketoprak | Ketoprak Energy | Powered by ketoprak, unstoppable | +13% |
| King Ronaldo | SIUUUU | The GOAT never loses | +15% |

### Mythic Skills

| Card | Skill Name | Description | Bonus |
|------|-----------|-------------|-------|
| Ayam Madu Panggang | Juicy AF | So good it's distracting | +18% |
| Geol-geol | Geol Hypnosis | Hypnotizes opponent with the wiggle | +20% |
| Linggis RGB | RGB Supremacy | RGB makes everything better, scientifically proven | +22% |
| Gold Lil Nas | Old Town Road | Been riding for too long, can't be stopped | +20% |

### Special Skills

| Card | Skill Name | Description | Bonus |
|------|-----------|-------------|-------|
| Jesu Ankle Break | Ankle Snap | 9999 ATK speaks for itself | +50% |

---

## Win Formula

```python
base_prob   = rarity_weight[yours] / (rarity_weight[yours] + rarity_weight[theirs])
atk_mod     = (your_atk - opponent_atk) / 1000   # 100 ATK diff ≈ ±10%
skill_bonus = card["skill"]["bonus"] if card["skill"] else 0
final_prob  = max(0.05, min(0.95, base_prob + atk_mod + skill_bonus))
```

- **Base prob** preserves the existing rarity-favors-higher feel
- **ATK mod** makes individual cards within the same rarity feel different (max swing ±10% between non-special cards)
- **Skill bonus** rewards higher rarity with passive power
- **Clamp 0.05–0.95** ensures upsets are always possible — no card is unbeatable

Special card (ATK 9999) gets clamped to 0.95 max.

---

## Duel Embed Display

Show both cards' ATK and skill in the duel result embed:

```
⚔️ Duel: Ariq vs Budi

🟡 King Ronaldo  (ATK: 88)
   ✨ SIUUUU — the GOAT never loses (+15%)

vs

🟣 Owo Sigma  (ATK: 67)
   ✨ Sigma Grindset — never stops grinding (+9%)

🏆 King Ronaldo menang!
```

Cards with no skill show only the ATK line, no skill line.

---

## Files Changed

- `config.py` — add `"atk"` and `"skill"` to every card in `CARDS`
- `bot.py` — update duel logic to use new formula; update duel embed to show ATK + skill
