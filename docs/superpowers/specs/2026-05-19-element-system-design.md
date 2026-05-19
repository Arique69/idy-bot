# Element System Design

**Date:** 2026-05-19  
**Status:** Approved

---

## Overview

Add a goofy element system to IDY Bot's card game. Each card has one element. Elements create type matchups that apply a small win chance modifier (+5%) in duels. Elements are displayed wherever cards are shown.

---

## Elements

| Element  | Emoji | Vibe                          |
|----------|-------|-------------------------------|
| Ngantuk  | 😴    | Lazy, sleepy, low energy      |
| Nyocot   | 🗣️    | Loud, talking nonsense, drama |
| Baper    | 😭    | Emotional, crybaby, sensitive |
| Sigma    | 😎    | Cool, grindset, unbothered    |
| Pejuang  | ⚔️    | Warrior, PSHT energy          |
| Lapar    | 🍗    | Hungry, food-motivated        |
| Rusdi    | 🤙    | Rusdi-coded, chaotic neutral  |
| Misteri  | 🌀    | Unknown, unpredictable        |

---

## Type Matchups

Attacker with advantage gains **+0.05** to win chance (before min/max clamp).

| Attacker | Defender | Reason                              |
|----------|----------|-------------------------------------|
| Sigma    | Baper    | Sigma doesn't care about feelings   |
| Baper    | Nyocot   | Drama shuts up the talker           |
| Nyocot   | Ngantuk  | Nonstop talking wakes you up        |
| Ngantuk  | Pejuang  | Too tired to train                  |
| Pejuang  | Sigma    | Grind has physical limits           |
| Pejuang  | Lapar    | Training beats hunger               |
| Lapar    | Nyocot   | Hungry man is dangerous             |
| Lapar    | Baper    | Hunger overrides emotion            |
| Lapar    | Ngantuk  | Can't sleep when starving           |
| Rusdi    | Misteri  | Rusdi always finds out              |

### Misteri Special Rule
When Misteri has a type disadvantage, it has a **20% chance to dodge** the penalty (the +0.05 is not applied to the opponent).

---

## Card Element Assignments

### Common
| Card                        | Element  |
|-----------------------------|----------|
| Halah Nyocot                | Nyocot   |
| Pura-pura ga liat           | Misteri  |
| Ngabuburit yuk              | Lapar    |
| Malas Banget                | Ngantuk  |
| Nguwawor                    | Ngantuk  |
| Andriana PSHT               | Pejuang  |
| Tolong dijelaskan           | Baper    |
| Pegi Kau Suki               | Nyocot   |
| Lebaran                     | Lapar    |
| Bohong                      | Nyocot   |
| Selamat Berbuka             | Lapar    |
| Admin Telah Tiba            | Sigma    |
| Rusdi Kapan yh              | Rusdi    |
| My Bini                     | Baper    |
| Rusdi Alamak                | Rusdi    |
| Captain Amba                | Pejuang  |
| SHSC PSHT                   | Pejuang  |
| Kewer-Kewer Sopan           | Misteri  |
| Yes King                    | Sigma    |
| Ladesh Pelatihan Ketat      | Pejuang  |
| Amba Gua Lagi Yang Kena     | Baper    |

### Rare
| Card                            | Element  |
|---------------------------------|----------|
| Bertolak Belakang               | Misteri  |
| Bercyanda                       | Nyocot   |
| Bodo Amat                       | Sigma    |
| Laba-laba Sunda                 | Misteri  |
| Spongebob Tuff                  | Pejuang  |
| Idy Dame yo                     | Baper    |
| Malas                           | Ngantuk  |
| Pak Cik Peduli?                 | Misteri  |
| Sengaja Ya Buat Aku Marah       | Baper    |
| Gelombang Laut                  | Misteri  |
| Amba Menangis                   | Baper    |
| Mana Buktinya                   | Nyocot   |
| Pilot Amba                      | Sigma    |
| Rewel Cipok                     | Nyocot   |
| Bobok                           | Ngantuk  |
| Ayah Tidur                      | Ngantuk  |

### Epic
| Card                            | Element  |
|---------------------------------|----------|
| Sodara                          | Rusdi    |
| Kenapa?                         | Baper    |
| Rusdi Balon                     | Rusdi    |
| Mahkota Mu King                 | Sigma    |
| Owo Swag                        | Sigma    |
| Menggugah Selera                | Lapar    |
| Solo Baca Buku                  | Sigma    |
| Ape pula bodoh nih              | Nyocot   |
| Tertawa Tapi Teluka             | Baper    |
| Terompet Pemanggil Pasukan      | Pejuang  |
| Owo Sigma                       | Sigma    |

### Legendary
| Card                                | Element  |
|-------------------------------------|----------|
| Toyota Supra 2000HP BRAkTAKTAK      | Pejuang  |
| Merah                               | Baper    |
| Tirai Misterius                     | Misteri  |
| Solo Swag                           | Sigma    |
| Rusdi nah ini                       | Rusdi    |
| Rusdi Informasi Palsu               | Rusdi    |
| Dimas Ketoprak                      | Lapar    |
| King Ronaldo                        | Sigma    |

### Mythic
| Card              | Element  |
|-------------------|----------|
| Ayam Madu Panggang | Lapar   |
| Geol-geol          | Misteri |
| Linggis RGB        | Pejuang |
| Gold Lil Nas       | Sigma   |

### Special
| Card              | Element  |
|-------------------|----------|
| Jesu Ankle Break  | Pejuang  |

---

## Code Changes

### `config.py`
- Add `"element": "<name>"` field to every card dict.
- Add `ELEMENTS` dict mapping element name → `{"emoji": ..., "label": ...}`.
- Add `ELEMENT_ADVANTAGES` dict: `{attacker: [list of defenders it beats]}`.

### `bot.py` — `compute_win_chance`
- After current calculation, check if card_a's element beats card_b's element → add 0.05.
- Check if card_b's element beats card_a's element:
  - If card_b is Misteri: 20% chance to dodge (skip the +0.05 for card_b).
  - Otherwise: add 0.05 to card_b side (subtract from card_a's effective chance).
- Apply existing `max(0.05, min(0.95, ...))` clamp last.

### Display locations
1. **Card pull embed** (`_build_card_embed`) — add element emoji + name line.
2. **`/kartu` preview** — add element line to card detail.
3. **Duel embed** (`card_field`) — add element line per card.

### `announce.txt`
- Write announcement explaining the new element system, list the 8 elements and their matchups in a fun tone.

---

## Out of Scope
- Element-based filtering in `/koleksi`
- Choosing which card to use in duel (duel still uses random card from collection)
- Multiple elements per card
