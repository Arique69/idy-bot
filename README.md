# Idy Bot 🎴

Discord bot gacha kartu GIF. Ketik `idy` di chat, bot bakal reply dengan kartu random berdasarkan sistem rarity.

---

## Cara Pakai

Ketik **`idy`** di channel mana aja → bot reply dengan kartu gacha.

---

## Sistem Rarity

| Rarity | Emoji | Drop Rate | Jumlah Kartu |
|--------|-------|-----------|--------------|
| Common | ⚪ | 23% | 12 |
| Rare | 🔵 | 23% | 7 |
| Epic | 🟣 | 23% | 4 |
| Legendary | 🟡 | 23% | 3 |
| Mythic | 🔴 | 8% | 1 |
| **Total** | | **100%** | **27** |

### Pity System
Kalau dapet **Common 3x berturut-turut**, pull berikutnya dijamin **Rare ke atas**. Footer embed bakal muncul `🍀 Pity activated!` kalau pity aktif.

---

## Slash Commands

| Command | Fungsi |
|---------|--------|
| `/koleksi` | Lihat semua kartu unik yang pernah kamu dapet, dikelompokkan per rarity |
| `/leaderboard` | Top 5 user dengan kartu Legendary & Mythic terbanyak |
| `/cuaca` | Cek cuaca hari ini di Jakarta |

---

## Struktur File

```
idy-bot/
├── bot.py        # Main bot, event handler, slash commands
├── config.py     # Konfigurasi rarity & daftar kartu
├── data.py       # Load/save data user ke data.json
├── data.json     # Data user (koleksi, streak, count) — tidak di-push ke git
└── .env          # Discord token — tidak di-push ke git
```

---

## Nambahin Kartu

Edit `config.py`, tambahin entry baru di list `CARDS`:

```python
{
    "url": "https://link-gif.gif",
    "name": "Nama Kartu",
    "rarity": "common",  # common / rare / epic / legendary / mythic
},
```

---

## Setup

### 1. Buat Discord Bot

1. Buka <https://discord.com/developers/applications> → **New Application**
2. Tab **Bot** → **Reset Token**, copy tokennya
3. Aktifkan **Message Content Intent** di tab Bot → Privileged Gateway Intents
4. **OAuth2 → URL Generator** → centang `bot` + permissions `Send Messages` & `Read Message History` → invite ke server

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Python 3.10+ diperlukan.

### 3. Buat file `.env`

```
DISCORD_TOKEN=token_discord_kamu
```

### 4. Jalankan Bot

```bash
python bot.py
```

> `data.json` akan otomatis terbuat saat bot pertama kali jalan.

---

## Format Log

```
2026-05-07 12:01:23 [INFO] Trigger | 2026-05-07 12:01:23 UTC | guild=My Server channel=#general user=someone
2026-05-07 12:01:23 [INFO] Card pulled | Solo Swag | rarity=legendary | pity=False
```
