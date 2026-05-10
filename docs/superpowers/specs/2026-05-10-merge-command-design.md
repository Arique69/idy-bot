# /merge Command Design

**Date:** 2026-05-10

## Overview

Add a `/merge` command that lets users combine 2 duplicate copies of a card to evolve it into a random card of the next rarity up.

## Rules

- **Cost:** 2 copies consumed per merge
- **Minimum owned:** User must own **at least 3 copies** to merge (keeps at least 1 after consuming 2)
- **Result:** 1 random card from the next rarity pool added to collection
- **Mythic blocked:** Mythic is max rarity — merging mythic cards is not allowed

## Rarity Evolution Chain

```
common → rare → epic → legendary → mythic
```

## Command

`/merge kartu:<card_name>`

- Single parameter with autocomplete
- Autocomplete filters to cards the user owns **3 or more copies of**, excluding mythics
- Merge executes immediately (no confirmation step)

## Merge Logic

1. Validate: card exists in collection with count ≥ 3; card is not mythic
2. Consume 2 copies: `collection[card_name] -= 2`
3. Determine next rarity from the chain above
4. Pick a random card from `CARDS` filtered to that next rarity
5. Add 1 copy to collection: `collection[result_name] += 1`
6. If result rarity is `legendary`, increment `user["legendary_count"]`
7. If result rarity is `mythic`, increment `user["mythic_count"]`
8. Save data

## Error Cases

| Condition | Response |
|-----------|----------|
| Card not owned or count < 3 | Ephemeral: `"Kamu butuh minimal 3 kartu {name} buat merge!"` |
| Card is mythic | Ephemeral: `"Mythic adalah rarity tertinggi, ga bisa di-merge!"` |

## Result Display (2 embeds)

**Embed 1 — Source card**
- Title: `"🔀 Kartu yang di-merge"`
- Description: `"{emoji} **{card_name}** x2\n\`{rarity_label}\``
- Color: source card's rarity color
- Image: source card's URL

**Embed 2 — Evolved result**
- Title: `"✨ Hasil Evolusi!"`
- Description: `"{emoji} **{result_name}**\n\`{result_label}\``
- Color: result card's rarity color
- Image: result card's URL
- Footer: `"2x {card_name} → {result_label}"`

## Files Changed

| File | Change |
|------|--------|
| `bot.py` | Add `/merge` command + autocomplete |
