"""Bot configuration: trigger word, GIF card pool, and rarity system."""

from __future__ import annotations

TRIGGER_WORD: str = "idy"

RARITY_CONFIG: dict = {
    "common":    {"emoji": "⚪", "color": 0x95a5a6, "label": "Common",    "shout": "Dapet kartu..."},
    "rare":      {"emoji": "🔵", "color": 0x3498db, "label": "Rare",      "shout": "✨ Rare Pull!"},
    "epic":      {"emoji": "🟣", "color": 0x9b59b6, "label": "Epic",      "shout": "🌟 EPIC PULL!"},
    "legendary": {"emoji": "🟡", "color": 0xf1c40f, "label": "Legendary", "shout": "💫 LEGENDARY!!!"},
    "mythic":    {"emoji": "🔴", "color": 0xe74c3c, "label": "MYTHIC",    "shout": "🔥 MYTHIC!!!! 🔥"},
}

CARDS: list[dict] = [
    # --- Common ⚪ ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODQ2OGRwcWxxMW53bWJwMW5seXRvY281N3E2OWtscGRkYnd4cjhlMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TPURLKJjqYNyjb4Q2K/giphy.gif",
        "name": "Jomok Biasa Aja",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODQ2OGRwcWxxMW53bWJwMW5seXRvY281N3E2OWtscGRkYnd4cjhlMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wgQTGjJMReIsbLnB3G/giphy.gif",
        "name": "PHP Ringan",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3N2xvejd3ZHF6Yms1d3V0NWR1Z2IzMHdnNXA3eTljZTl4c3RsNG13YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/VBcO3pX9s9rs5H29DD/giphy.gif",
        "name": "Cuma Temenan Kok",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3emYyNW9maWtheXV5ZjI2MXhxZnpkeGR6dXltdmptcnRyeWQ1b2RmdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/anec64aGGWj3KZ1iP4/giphy.gif",
        "name": "Gebetan Zonk",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZWhrNDc0NTc4b3pvZXdsNDBmM3FuZjRiM2FhemViZjI3MDE5MTJ1NCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xjB29zEPeUogVR9Hha/giphy.gif",
        "name": "Modus Gagal",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/Ihx6bbytRTEiQ7e4xF/giphy.gif",
        "name": "Pengen Tapi Gak Jadi",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/jsLf2ALAjO8g7mpmt0/giphy.gif",
        "name": "Cringe Level 1",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/5PSwLEcp5qvlFtGasw/giphy.gif",
        "name": "Jomok Pemula",
        "rarity": "common",
    },
    # --- Rare 🔵 ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xz0qNZfJM3XeKznwVq/giphy.gif",
        "name": "Modus Berbahaya",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9oryRGyTdzzFEBUgcb/giphy.gif",
        "name": "PHP Master",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/VwNySHxfzhksbDnR0v/giphy.gif",
        "name": "Jomok Terlatih",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/gNjSEUHYeGVAiSRwyt/giphy.gif",
        "name": "Jomok Spesialis",
        "rarity": "rare",
    },
    # --- Epic 🟣 ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QGyYIduiYf1zUkFHfR/giphy.gif",
        "name": "The Cringe Lord",
        "rarity": "epic",
    },
    {
        "url": "https://media.giphy.com/media/bTnjjJn4pJLFUa0CLP/giphy.gif",
        "name": "Jomok Awakened",
        "rarity": "epic",
    },
    # --- Legendary 🟡 ---
    {
        "url": "https://media.giphy.com/media/iiCQrGn7lEiWXF7fxe/giphy.gif",
        "name": "Jomok Abadi",
        "rarity": "legendary",
    },
]
