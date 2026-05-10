# Card Power System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `power` stat to every card and use it in `/duel` via weighted-random win probability, pulling cards from each player's collection.

**Architecture:** Two files change — `config.py` gets a `"power"` field added to every card dict, and `bot.py` gets a new `get_random_collection_card()` helper plus updated duel logic and embed. No data.json schema changes needed.

**Tech Stack:** Python 3, discord.py, existing `data.py` helpers

---

### Task 1: Add `power` field to all cards in config.py

**Files:**
- Modify: `config.py`

Default power by rarity: common=100, rare=250, epic=450, legendary=700, mythic=900.

The safest edit strategy is to find each card's `"rarity": "<value>"` line and add `"power": <value>` on the next line. Do NOT rewrite whole card dicts — only add the missing field to avoid URL corruption.

- [ ] **Step 1: Add `"power"` to all Common cards**

In `config.py`, for every card dict that has `"rarity": "common"`, add `"power": 100` as a new key. There are 21 common cards:
`Halah Nyocot`, `Pura-pura ga liat`, `Ngabuburit yuk`, `Malas Banget`, `Nguwawor`, `Andriana PSHT`, `Tolong dijelaskan`, `Pegi Kau Suki`, `Lebaran`, `Bohong`, `Selamat Berbuka`, `Admin Telah Tiba`, `Rusdi Kapan yh`, `My Bini`, `Rusdi Alamak`, `Captain Amba`, `SHSC PSHT`, `Kewer-Kewer Sopan`, `Yes King`, `Ladesh Pelatihan Ketat`, `Amba Gua Lagi Yang Kena`.

Each dict should look like:
```python
{
    "url": "...",
    "name": "Halah Nyocot",
    "rarity": "common",
    "power": 100,
},
```

- [ ] **Step 2: Add `"power"` to all Rare cards**

For every card with `"rarity": "rare"`, add `"power": 250`. There are 11 rare cards:
`Idy Dame yo`, `Malas`, `Pak Cik Peduli?`, `Sengaja Ya Buat Aku Marah`, `Gelombang Laut`, `Amba Menangis`, `Mana Buktinya`, `Pilot Amba`, `Rewel Cipok`, `Bobok`, `Ayah Tidur`.

- [ ] **Step 3: Add `"power"` to all Epic cards**

For every card with `"rarity": "epic"`, add `"power": 450`. There are 8 epic cards:
`Mahkota Mu King`, `Owo Swag`, `Menggugah Selera`, `Solo Baca Buku`, `Ape pula bodoh nih`, `Tertawa Tapi Teluka`, `Terompet Pemanggil Pasukan`, `Owo Sigma`.

- [ ] **Step 4: Add `"power"` to all Legendary cards**

For every card with `"rarity": "legendary"`, add `"power": 700`. There are 6 legendary cards:
`Tirai Misterius`, `Solo Swag`, `Rusdi  nah ini`, `Rusdi Informasi Palsu`, `Dimas Ketoprak`, `King Ronaldo`.

- [ ] **Step 5: Add `"power"` to all Mythic cards**

For every card with `"rarity": "mythic"`, add `"power": 900`. There are 4 mythic cards:
`Ayam Madu Panggang`, `Geol-geol`, `Linggis RGB`, `Gold Lil Nas`.

- [ ] **Step 6: Verify all 50 cards have `power`**

```bash
python -c "from config import CARDS; missing = [c['name'] for c in CARDS if 'power' not in c]; print('Missing:', missing or 'None'); print('Total cards:', len(CARDS))"
```
Expected output:
```
Missing: None
Total cards: 50
```

- [ ] **Step 7: Commit**

```bash
git add config.py
git commit -m "feat: add power stat to all cards"
```

---

### Task 2: Add `get_random_collection_card()` and update duel in bot.py

**Files:**
- Modify: `bot.py`

- [ ] **Step 1: Add `get_random_collection_card()` after `pull_card_simple()`**

Insert this function after the `pull_card_simple` function (after line 87):

```python
def get_random_collection_card(user_id: int) -> dict | None:
    """Return a random card dict from the user's collection, or None if empty."""
    data = load_data()
    user = get_user(data, str(user_id))
    owned = [name for name, count in user.get("collection", {}).items() if count > 0]
    if not owned:
        return None
    card_name = random.choice(owned)
    return next((c for c in CARDS if c["name"] == card_name), None)
```

- [ ] **Step 2: Replace the duel command body**

Find the `async def duel(` command (around line 368). Replace the entire function body (everything from `if lawan.bot:` through `await interaction.response.send_message(embed=embed)`) with:

```python
        if lawan.bot:
            await interaction.response.send_message("Ga bisa duel sama bot!", ephemeral=True)
            return
        if lawan.id == interaction.user.id:
            await interaction.response.send_message("Ga bisa duel sama diri sendiri!", ephemeral=True)
            return

        card_a = get_random_collection_card(interaction.user.id)
        card_b = get_random_collection_card(lawan.id)

        if card_a is None:
            await interaction.response.send_message(
                "Kamu belum punya kartu! Ketik `idy` buat dapet kartu dulu.", ephemeral=True
            )
            return
        if card_b is None:
            await interaction.response.send_message(
                f"**{lawan.display_name}** belum punya kartu!", ephemeral=True
            )
            return

        power_a = card_a.get("power", 100)
        power_b = card_b.get("power", 100)
        win_chance_a = power_a / (power_a + power_b)

        cfg_a = RARITY_CONFIG[card_a["rarity"]]
        cfg_b = RARITY_CONFIG[card_b["rarity"]]

        data = load_data()
        user_a = get_user(data, str(interaction.user.id))
        user_b = get_user(data, str(lawan.id))

        if random.random() < win_chance_a:
            result = f"🏆 **{interaction.user.display_name}** menang!"
            color = 0x2ecc71
            user_a["duel_wins"] += 1
            user_b["duel_losses"] += 1
        else:
            result = f"🏆 **{lawan.display_name}** menang!"
            color = 0xe74c3c
            user_b["duel_wins"] += 1
            user_a["duel_losses"] += 1

        save_data(data)

        pct_a = win_chance_a * 100
        pct_b = 100 - pct_a

        embed = discord.Embed(title="⚔️ DUEL KARTU!", description=result, color=color)
        embed.add_field(
            name=f"{interaction.user.display_name}",
            value=f"{cfg_a['emoji']} **{card_a['name']}**\n`{cfg_a['label']}`\n⚡ {power_a}",
            inline=True,
        )
        embed.add_field(name="VS", value="⚔️", inline=True)
        embed.add_field(
            name=f"{lawan.display_name}",
            value=f"{cfg_b['emoji']} **{card_b['name']}**\n`{cfg_b['label']}`\n⚡ {power_b}",
            inline=True,
        )
        embed.set_footer(text=f"Peluang menang: {pct_a:.1f}% vs {pct_b:.1f}% • Kartu diambil dari koleksi")

        await interaction.response.send_message(embed=embed)
```

- [ ] **Step 3: Remove `pull_card_simple()` — it is no longer used**

Delete the entire `pull_card_simple` function from `bot.py` (lines ~79–87):
```python
def pull_card_simple() -> dict:
    """Pull a card without affecting user data (for duel)."""
    rarities = list(RARITY_CONFIG.keys())
    weights = [RARITY_CONFIG[r]["weight"] for r in rarities]
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
    pool = [c for c in CARDS if c["rarity"] == chosen_rarity]
    if not pool:
        pool = CARDS
    return random.choice(pool)
```

Also remove the now-unused variables `rank_a`, `rank_b` if they remain anywhere in duel (they should be gone after Step 2).

- [ ] **Step 4: Verify syntax**

```bash
python -m py_compile bot.py && echo "OK"
```
Expected: `OK`

- [ ] **Step 5: Verify no leftover references to `pull_card_simple`**

```bash
python -c "src=open('bot.py').read(); print('pull_card_simple refs:', src.count('pull_card_simple'))"
```
Expected: `pull_card_simple refs: 0`

- [ ] **Step 6: Commit**

```bash
git add bot.py
git commit -m "feat: duel uses collection cards with power-based win probability"
```
