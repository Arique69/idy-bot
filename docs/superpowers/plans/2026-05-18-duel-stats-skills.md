# Duel Stats & Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ATK stats and passive skills to every card so duels feel less random — individual cards matter while upsets remain possible.

**Architecture:** Each card in `config.py` gets a deterministic `"atk"` field (seeded from card name) and a `"skill"` field (None for common/rare, handcrafted dict for epic+). The duel command in `bot.py` uses a new `compute_win_chance()` helper that layers ATK difference and skill bonus on top of the existing rarity-based probability. The embed is updated to show each card's ATK and skill.

**Tech Stack:** Python 3.8, discord.py, pytest (new)

---

## File Map

- Modify: `config.py` — add `_atk()` helper before `CARDS`, add `"atk"` and `"skill"` fields to every card entry
- Modify: `bot.py` — add module-level `compute_win_chance()` function; replace duel logic at lines 403–415 and embed at lines 432–447
- Create: `tests/test_duel.py` — unit tests for `compute_win_chance()`
- Modify: `requirements.txt` — add `pytest` if not present

---

## Task 1: Add ATK generation helper to config.py

**Files:**
- Modify: `config.py` (before line 16 where `CARDS` is defined)

- [ ] **Step 1: Add `_atk()` helper directly above the `CARDS` list**

Insert this block between the `RARITY_CONFIG` dict and the `CARDS = [` line:

```python
def _atk(name: str, rarity: str) -> int:
    _ranges = {
        "common": (10, 30), "rare": (25, 50), "epic": (45, 75),
        "legendary": (65, 95), "mythic": (85, 110), "special": (9999, 9999),
    }
    lo, hi = _ranges[rarity]
    if lo == hi:
        return lo
    return sum(ord(c) for c in name) % (hi - lo + 1) + lo
```

- [ ] **Step 2: Add `"atk"` and `"skill": None` to every common card**

For each common card entry, add two new fields. Example transformation:

```python
# Before:
{
    "url": "https://...",
    "name": "Halah Nyocot",
    "rarity": "common",
    "power": 100,
},

# After:
{
    "url": "https://...",
    "name": "Halah Nyocot",
    "rarity": "common",
    "power": 100,
    "atk": _atk("Halah Nyocot", "common"),
    "skill": None,
},
```

Apply to all 21 common cards:
- `"Halah Nyocot"`, `"Pura-pura ga liat"`, `"Ngabuburit yuk"`, `"Malas Banget"`, `"Nguwawor"`, `"Andriana PSHT"`, `"Tolong dijelaskan"`, `"Pegi Kau Suki"`, `"Lebaran"`, `"Bohong"`, `"Selamat Berbuka"`, `"Admin Telah Tiba"`, `"Rusdi Kapan yh"`, `"My Bini"`, `"Rusdi Alamak"`, `"Captain Amba"`, `"SHSC PSHT"`, `"Kewer-Kewer Sopan"`, `"Yes King"`, `"Ladesh Pelatihan Ketat"`, `"Amba Gua Lagi Yang Kena"`

- [ ] **Step 3: Add `"atk"` and `"skill": None` to every rare card**

Apply the same pattern to all 16 rare cards:
- `"Bertolak Belakang"`, `"Bercyanda"`, `"Bodo Amat"`, `"Laba-laba Sunda"`, `"Spongebob Tuff"`, `"Idy Dame yo"`, `"Malas"`, `"Pak Cik Peduli?"`, `"Sengaja Ya Buat Aku Marah"`, `"Gelombang Laut"`, `"Amba Menangis"`, `"Mana Buktinya"`, `"Pilot Amba"`, `"Rewel Cipok"`, `"Bobok"`, `"Ayah Tidur"`

- [ ] **Step 4: Verify ATK values are computed correctly**

Run:
```bash
python -c "from config import CARDS; print([(c['name'], c['atk']) for c in CARDS if c['rarity'] in ('common','rare')])"
```

Expected: a list of (name, integer) pairs where all common ATKs are 10–30 and all rare ATKs are 25–50. No errors.

- [ ] **Step 5: Commit**

```bash
git add config.py
git commit -m "Add ATK stats to common and rare cards"
```

---

## Task 2: Add ATK and skills to epic, legendary, mythic, special cards

**Files:**
- Modify: `config.py`

- [ ] **Step 1: Add ATK + skills to all 11 epic cards**

```python
# Sodara
"atk": _atk("Sodara", "epic"),
"skill": {"name": "Koneksi Sodara", "desc": "Family pulls strings behind the scenes", "bonus": 0.08},

# Kenapa?
"atk": _atk("Kenapa?", "epic"),
"skill": {"name": "Pertanyaan Filosofis", "desc": "Opponent is too confused to focus", "bonus": 0.06},

# Rusdi Balon
"atk": _atk("Rusdi Balon", "epic"),
"skill": {"name": "Melayang", "desc": "Floats above the conflict", "bonus": 0.07},

# Mahkota Mu King
"atk": _atk("Mahkota Mu King", "epic"),
"skill": {"name": "Aura Raja", "desc": "Royal presence intimidates opponent", "bonus": 0.10},

# Owo Swag
"atk": _atk("Owo Swag", "epic"),
"skill": {"name": "Too Swag", "desc": "Opponent can't help but be impressed", "bonus": 0.08},

# Menggugah Selera
"atk": _atk("Menggugah Selera", "epic"),
"skill": {"name": "Lapar Duluan", "desc": "Makes opponent hungry, loses focus", "bonus": 0.07},

# Solo Baca Buku
"atk": _atk("Solo Baca Buku", "epic"),
"skill": {"name": "Galaxy Brain", "desc": "Big brain moves", "bonus": 0.09},

# Ape pula bodoh nih
"atk": _atk("Ape pula bodoh nih", "epic"),
"skill": {"name": "Dismissal Aura", "desc": "So annoying opponent ragequits early", "bonus": 0.06},

# Tertawa Tapi Teluka
"atk": _atk("Tertawa Tapi Teluka", "epic"),
"skill": {"name": "Trauma Tertawa", "desc": "Hides pain with laughter, catches opponent off guard", "bonus": 0.08},

# Terompet Pemanggil Pasukan
"atk": _atk("Terompet Pemanggil Pasukan", "epic"),
"skill": {"name": "Backup Datang!", "desc": "Calls the whole squad", "bonus": 0.12},

# Owo Sigma
"atk": _atk("Owo Sigma", "epic"),
"skill": {"name": "Sigma Grindset", "desc": "Never stops grinding", "bonus": 0.09},
```

- [ ] **Step 2: Add ATK + skills to all 8 legendary cards**

Note: `"Rusdi  nah ini"` has a double space — match the name exactly as it appears in config.py.

```python
# Toyota Supra 2000HP BRAkTAKTAK
"atk": _atk("Toyota Supra 2000HP BRAkTAKTAK", "legendary"),
"skill": {"name": "2000HP Drift", "desc": "Goes BRAKTAKTAK and overtakes everything", "bonus": 0.15},

# Merah
"atk": _atk("Merah", "legendary"),
"skill": {"name": "Murka Merah", "desc": "Rage mode activated", "bonus": 0.13},

# Tirai Misterius
"atk": _atk("Tirai Misterius", "legendary"),
"skill": {"name": "Tirai Terbuka", "desc": "Nobody knows what's behind", "bonus": 0.12},

# Solo Swag
"atk": _atk("Solo Swag", "legendary"),
"skill": {"name": "Solo Mode ON", "desc": "Locked in, impossible to distract", "bonus": 0.14},

# Rusdi  nah ini  (double space — match exactly)
"atk": _atk("Rusdi  nah ini", "legendary"),
"skill": {"name": "Udah Nah Ini", "desc": "When Rusdi says this, it's over", "bonus": 0.13},

# Rusdi Informasi Palsu
"atk": _atk("Rusdi Informasi Palsu", "legendary"),
"skill": {"name": "Hoaks Tersebar", "desc": "Opponent believes fake news and panics", "bonus": 0.11},

# Dimas Ketoprak
"atk": _atk("Dimas Ketoprak", "legendary"),
"skill": {"name": "Ketoprak Energy", "desc": "Powered by ketoprak, unstoppable", "bonus": 0.13},

# King Ronaldo
"atk": _atk("King Ronaldo", "legendary"),
"skill": {"name": "SIUUUU", "desc": "The GOAT never loses", "bonus": 0.15},
```

- [ ] **Step 3: Add ATK + skills to all 4 mythic cards**

```python
# Ayam Madu Panggang
"atk": _atk("Ayam Madu Panggang", "mythic"),
"skill": {"name": "Juicy AF", "desc": "So good it's distracting", "bonus": 0.18},

# Geol-geol
"atk": _atk("Geol-geol", "mythic"),
"skill": {"name": "Geol Hypnosis", "desc": "Hypnotizes opponent with the wiggle", "bonus": 0.20},

# Linggis RGB
"atk": _atk("Linggis RGB", "mythic"),
"skill": {"name": "RGB Supremacy", "desc": "RGB makes everything better, scientifically proven", "bonus": 0.22},

# Gold Lil Nas
"atk": _atk("Gold Lil Nas", "mythic"),
"skill": {"name": "Old Town Road", "desc": "Been riding for too long, can't be stopped", "bonus": 0.20},
```

- [ ] **Step 4: Add ATK + skill to special card**

```python
# Jesu Ankle Break
"atk": 9999,
"skill": {"name": "Ankle Snap", "desc": "9999 ATK speaks for itself", "bonus": 0.50},
```

- [ ] **Step 5: Verify all cards have atk and skill fields**

Run:
```bash
python -c "
from config import CARDS
missing = [c['name'] for c in CARDS if 'atk' not in c or 'skill' not in c]
print('Missing fields:', missing or 'none')
epic_plus = [c for c in CARDS if c['rarity'] in ('epic','legendary','mythic','special')]
no_skill = [c['name'] for c in epic_plus if c['skill'] is None]
print('Epic+ missing skill:', no_skill or 'none')
"
```

Expected output:
```
Missing fields: none
Epic+ missing skill: none
```

- [ ] **Step 6: Commit**

```bash
git add config.py
git commit -m "Add ATK stats and goofy skills to epic/legendary/mythic/special cards"
```

---

## Task 3: Add `compute_win_chance()` helper + tests

**Files:**
- Create: `tests/test_duel.py`
- Modify: `bot.py` (add function before the `IDYBot` class)
- Modify: `requirements.txt`

- [ ] **Step 1: Add pytest to requirements.txt if not already there**

Check `requirements.txt`. If `pytest` is not in it, add it:
```
pytest
```

- [ ] **Step 2: Create `tests/` directory and write failing tests**

Create `tests/__init__.py` (empty file) and `tests/test_duel.py`:

```python
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

def test_result_clamped_between_005_and_095():
    mythic  = {"rarity": "mythic",  "atk": 110, "skill": {"name": "X", "desc": "Y", "bonus": 0.22}}
    common  = {"rarity": "common",  "atk": 10,  "skill": None}
    assert compute_win_chance(mythic, common) == 0.95
    assert compute_win_chance(common, mythic) == 0.05
```

- [ ] **Step 3: Run tests — verify they fail with ImportError**

```bash
python -m pytest tests/test_duel.py -v
```

Expected: `ImportError: cannot import name 'compute_win_chance' from 'bot'`

- [ ] **Step 4: Add `compute_win_chance()` to bot.py**

Add this function at module level in `bot.py`, directly after the `RARITY_ORDER` list (after line 37):

```python
def compute_win_chance(card_a: dict, card_b: dict) -> float:
    rank_a = RARITY_ORDER.index(card_a["rarity"])
    rank_b = RARITY_ORDER.index(card_b["rarity"])
    gap = rank_a - rank_b
    base = 0.5 + gap * 0.15
    atk_mod = (card_a["atk"] - card_b["atk"]) / 1000
    skill_bonus = card_a["skill"]["bonus"] if card_a.get("skill") else 0
    return max(0.05, min(0.95, base + atk_mod + skill_bonus))
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
python -m pytest tests/test_duel.py -v
```

Expected:
```
tests/test_duel.py::test_same_rarity_same_atk_is_50_50 PASSED
tests/test_duel.py::test_same_rarity_higher_atk_wins_more PASSED
tests/test_duel.py::test_skill_bonus_increases_chance PASSED
tests/test_duel.py::test_result_clamped_between_005_and_095 PASSED
4 passed
```

- [ ] **Step 6: Commit**

```bash
git add tests/ bot.py requirements.txt
git commit -m "Add compute_win_chance helper with ATK and skill logic, add tests"
```

---

## Task 4: Update duel command to use new formula and embed

**Files:**
- Modify: `bot.py:403–449`

- [ ] **Step 1: Replace the duel win logic block**

Find this block in `bot.py` (lines 403–415):

```python
            rank_a = RARITY_ORDER.index(card_a["rarity"])
            rank_b = RARITY_ORDER.index(card_b["rarity"])

            cfg_a = RARITY_CONFIG[card_a["rarity"]]
            cfg_b = RARITY_CONFIG[card_b["rarity"]]

            data = load_data()
            user_a = get_user(data, str(interaction.user.id))
            user_b = get_user(data, str(lawan.id))

            gap = rank_a - rank_b
            win_chance_a = min(0.9, max(0.1, 0.5 + gap * 0.15))
            a_wins = random.random() < win_chance_a
```

Replace with:

```python
            cfg_a = RARITY_CONFIG[card_a["rarity"]]
            cfg_b = RARITY_CONFIG[card_b["rarity"]]

            data = load_data()
            user_a = get_user(data, str(interaction.user.id))
            user_b = get_user(data, str(lawan.id))

            win_chance_a = compute_win_chance(card_a, card_b)
            a_wins = random.random() < win_chance_a
```

- [ ] **Step 2: Replace the embed block**

Find this block (lines 432–447):

```python
            embed = discord.Embed(title="⚔️ DUEL KARTU!", description=result, color=color)
            pct_a = win_chance_a * 100
            pct_b = 100 - pct_a
            embed.add_field(
                name=f"{interaction.user.display_name}",
                value=f"{cfg_a['emoji']} **{card_a['name']}**\n`{cfg_a['label']}`\n🎲 {pct_a:.0f}%",
                inline=True,
            )
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(
                name=f"{lawan.display_name}",
                value=f"{cfg_b['emoji']} **{card_b['name']}**\n`{cfg_b['label']}`\n🎲 {pct_b:.0f}%",
                inline=True,
            )
            embed.add_field(name="🃏 Winner Card", value=f"**{winner_card['name']}**", inline=False)
            embed.set_image(url=winner_card["url"])
```

Replace with:

```python
            embed = discord.Embed(title="⚔️ DUEL KARTU!", description=result, color=color)
            pct_a = win_chance_a * 100
            pct_b = 100 - pct_a

            def card_field(card, cfg, pct):
                lines = [f"{cfg['emoji']} **{card['name']}**", f"`{cfg['label']}` | ⚔️ ATK {card['atk']}", f"🎲 {pct:.0f}%"]
                if card.get("skill"):
                    lines.append(f"✨ **{card['skill']['name']}** — {card['skill']['desc']} (+{card['skill']['bonus']*100:.0f}%)")
                return "\n".join(lines)

            embed.add_field(name=interaction.user.display_name, value=card_field(card_a, cfg_a, pct_a), inline=True)
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(name=lawan.display_name, value=card_field(card_b, cfg_b, pct_b), inline=True)
            embed.add_field(name="🃏 Winner Card", value=f"**{winner_card['name']}**", inline=False)
            embed.set_image(url=winner_card["url"])
```

- [ ] **Step 3: Run existing tests to confirm nothing broke**

```bash
python -m pytest tests/ -v
```

Expected: all 4 tests pass.

- [ ] **Step 4: Smoke test — start bot locally and run a duel**

```bash
python bot.py
```

In Discord, run `/duel @someone`. Verify:
- Both card fields show ATK value
- Epic+ cards show the skill line with name, description, and % bonus
- Common/rare cards show no skill line
- Winner card image appears
- No Python errors in console

- [ ] **Step 5: Commit**

```bash
git add bot.py
git commit -m "Use compute_win_chance in duel; show ATK and skill in embed"
```
