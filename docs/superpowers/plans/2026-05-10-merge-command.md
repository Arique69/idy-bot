# /merge Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/merge` command that consumes 2 duplicate copies of a card and returns 1 random card of the next rarity up.

**Architecture:** Single file change — add `/merge` command and its autocomplete to `bot.py`, following the exact same patterns as `/gift` and `/trade`. A module-level `RARITY_NEXT` dict maps each rarity to the one above it.

**Tech Stack:** Python 3, discord.py, existing `data.py` helpers (`load_data`, `save_data`, `get_user`), existing `CARDS` and `RARITY_CONFIG` from `config.py`

---

### Task 1: Add `/merge` command to bot.py

**Files:**
- Modify: `D:\Dev\idy-bot\bot.py`

- [ ] **Step 1: Add `RARITY_NEXT` constant near the top of bot.py**

Insert after the `GUILD = discord.Object(...)` line:

```python
RARITY_NEXT = {
    "common": "rare",
    "rare": "epic",
    "epic": "legendary",
    "legendary": "mythic",
}
```

- [ ] **Step 2: Add the `/merge` command inside `setup_hook`, after the `/gift` command block**

Paste this entire block (the command + its autocomplete) after the `gift` autocomplete function, before `self.tree.copy_global_to(guild=GUILD)`:

```python
        @self.tree.command(name="merge", description="Gabungkan 2 kartu duplikat jadi kartu rarity lebih tinggi")
        @app_commands.describe(kartu="Kartu yang mau di-merge (harus punya minimal 3)")
        async def merge(interaction: discord.Interaction, kartu: str) -> None:
            data = load_data()
            user = get_user(data, str(interaction.user.id))

            card_obj = next((c for c in CARDS if c["name"] == kartu), None)
            if card_obj is None or user["collection"].get(kartu, 0) < 3:
                await interaction.response.send_message(
                    f"Kamu butuh minimal 3 kartu **{kartu}** buat merge!", ephemeral=True
                )
                return

            if card_obj["rarity"] == "mythic":
                await interaction.response.send_message(
                    "Mythic adalah rarity tertinggi, ga bisa di-merge!", ephemeral=True
                )
                return

            user["collection"][kartu] -= 2
            if user["collection"][kartu] <= 0:
                del user["collection"][kartu]

            next_rarity = RARITY_NEXT[card_obj["rarity"]]
            pool = [c for c in CARDS if c["rarity"] == next_rarity]
            result_card = random.choice(pool)
            user["collection"][result_card["name"]] = user["collection"].get(result_card["name"], 0) + 1

            if next_rarity == "legendary":
                user["legendary_count"] += 1
            elif next_rarity == "mythic":
                user["mythic_count"] += 1

            save_data(data)

            src_cfg = RARITY_CONFIG[card_obj["rarity"]]
            res_cfg = RARITY_CONFIG[next_rarity]

            embed_src = discord.Embed(
                title="🔀 Kartu yang di-merge",
                description=f"{src_cfg['emoji']} **{kartu}** x2\n`{src_cfg['label']}`",
                color=src_cfg["color"],
            )
            embed_src.set_image(url=card_obj["url"])

            embed_res = discord.Embed(
                title="✨ Hasil Evolusi!",
                description=f"{res_cfg['emoji']} **{result_card['name']}**\n`{res_cfg['label']}`",
                color=res_cfg["color"],
            )
            embed_res.set_image(url=result_card["url"])
            embed_res.set_footer(text=f"2x {kartu} → {res_cfg['label']}")

            await interaction.response.send_message(embeds=[embed_src, embed_res])

        @merge.autocomplete("kartu")
        async def merge_kartu_ac(interaction: discord.Interaction, current: str):
            data = load_data()
            user = get_user(data, str(interaction.user.id))
            results = []
            for name, cnt in user["collection"].items():
                if cnt < 3 or current.lower() not in name.lower():
                    continue
                card_obj = next((c for c in CARDS if c["name"] == name), None)
                if card_obj is None or card_obj["rarity"] == "mythic":
                    continue
                emoji = RARITY_CONFIG[card_obj["rarity"]]["emoji"]
                results.append(app_commands.Choice(name=f"{emoji} {name} (x{cnt})", value=name))
            return results[:25]
```

- [ ] **Step 3: Verify syntax**

```bash
python -m py_compile D:\Dev\idy-bot\bot.py && echo OK
```
Expected: `OK`

- [ ] **Step 4: Verify RARITY_NEXT and merge command are present**

```bash
python -c "import ast; src=open('D:/Dev/idy-bot/bot.py').read(); print('RARITY_NEXT:', 'RARITY_NEXT' in src); print('merge cmd:', 'name=\"merge\"' in src); print('merge_kartu_ac:', 'merge_kartu_ac' in src)"
```
Expected:
```
RARITY_NEXT: True
merge cmd: True
merge_kartu_ac: True
```

- [ ] **Step 5: Commit**

```bash
git add D:\Dev\idy-bot\bot.py
git commit -m "feat: add /merge command to evolve duplicate cards"
```
