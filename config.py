"""Bot configuration: trigger word, GIF card pool, and rarity system."""

from __future__ import annotations

TRIGGER_WORD: str = "idy"

RARITY_CONFIG: dict = {
    "common":    {"emoji": "⚪", "color": 0x95a5a6, "label": "Common",    "shout": "Dapet kartu...",    "weight": 22},
    "rare":      {"emoji": "🔵", "color": 0x3498db, "label": "Rare",      "shout": "✨ Rare Pull!",     "weight": 22},
    "epic":      {"emoji": "🟣", "color": 0x9b59b6, "label": "Epic",      "shout": "🌟 EPIC PULL!",    "weight": 22},
    "legendary": {"emoji": "🟡", "color": 0xf1c40f, "label": "Legendary", "shout": "💫 LEGENDARY!!!",  "weight": 22},
    "mythic":    {"emoji": "🔴", "color": 0xe74c3c, "label": "MYTHIC",    "shout": "🔥 MYTHIC!!!! 🔥", "weight":  8},
}

CARDS: list[dict] = [
    # --- Common ⚪ ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODQ2OGRwcWxxMW53bWJwMW5seXRvY281N3E2OWtscGRkYnd4cjhlMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TPURLKJjqYNyjb4Q2K/giphy.gif",
        "name": "Halah Nyocot",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODQ2OGRwcWxxMW53bWJwMW5seXRvY281N3E2OWtscGRkYnd4cjhlMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wgQTGjJMReIsbLnB3G/giphy.gif",
        "name": "Pura-pura ga liat",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3N2xvejd3ZHF6Yms1d3V0NWR1Z2IzMHdnNXA3eTljZTl4c3RsNG13YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/VBcO3pX9s9rs5H29DD/giphy.gif",
        "name": "Ngabuburit yuk",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3emYyNW9maWtheXV5ZjI2MXhxZnpkeGR6dXltdmptcnRyeWQ1b2RmdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/anec64aGGWj3KZ1iP4/giphy.gif",
        "name": "Malas Banget",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZWhrNDc0NTc4b3pvZXdsNDBmM3FuZjRiM2FhemViZjI3MDE5MTJ1NCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xjB29zEPeUogVR9Hha/giphy.gif",
        "name": "Nguwawor",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/Ihx6bbytRTEiQ7e4xF/giphy.gif",
        "name": "Andriana PSHT",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/jsLf2ALAjO8g7mpmt0/giphy.gif",
        "name": "Tolong dijelaskan",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/5PSwLEcp5qvlFtGasw/giphy.gif",
        "name": "Pegi Kau Suki",
        "rarity": "common",
    },
    {
        "url": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzBhMDQ4ZnZ3ZXFnMWxwYjE4eGVibjUydnlvdjVpeHBzcW5nbzdmbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/D5LIdoJaeUBIfJC1sj/giphy.gif",
        "name": "Lebaran",
        "rarity": "common",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExanM4YXVyY2MzdzFlNWxhbHhndXU4eTcxdjd0MjJ1N3YzYjFibjVmaiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/uizHrLgtExbmXRtPhp/giphy.gif",
        "name": "Bohong",
        "rarity": "common",
    },
    {
        "url": "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNG5udGJ5bGdmbG83dzByNWlnN24xN2p6c2F0MXZuNmUwb2gxYzRrYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/iadQidGpB8molTjslq/giphy.gif",
        "name": "Selamat Berbuka",
        "rarity": "common",
    },
    {
        "url": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXpmeGtoN2FkdzlzeDBtdnlkeW1udmV6N3dkaXlhMzBnaHZhYnQ2aSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6hEkOjy76BpkNG3K4p/giphy.gif",
        "name": "Admin Telah Tiba",
        "rarity": "common",
    },
    # --- Rare 🔵 ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xz0qNZfJM3XeKznwVq/giphy.gif",
        "name": "Malas",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9oryRGyTdzzFEBUgcb/giphy.gif",
        "name": "Amba Menangis",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/VwNySHxfzhksbDnR0v/giphy.gif",
        "name": "Mana Buktinya",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/gNjSEUHYeGVAiSRwyt/giphy.gif",
        "name": "Pilot Amba",
        "rarity": "rare",
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1501879984283717684/Screenshot_20260507_163251_TikTok.png?ex=69fe56fb&is=69fd057b&hm=41dca3836e6d370cdf6ac69e6c8c105f073bc9fa8d27b4b6d0d597dc475b67bb&=&format=webp&quality=lossless",
        "name": "Rewel Cipok",
        "rarity": "rare",
    },
    # --- Epic 🟣 ---
    {
        "url": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGF6OHZtbzBlMGttbGswMDJkYmFwbXozMW1ydHZncGhra2F6aTRhbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dgWteQuo1LXqlxiDJU/giphy.gif",
        "name": "Solo Baca Buku",
        "rarity": "epic",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QGyYIduiYf1zUkFHfR/giphy.gif",
        "name": "Ape pula bodoh nih",
        "rarity": "epic",
    },
    {
        "url": "https://media.giphy.com/media/bTnjjJn4pJLFUa0CLP/giphy.gif",
        "name": "Tertawa Tapi Teluka",
        "rarity": "epic",
    },
    # --- Legendary 🟡 ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnYwMjQxN2RpYm1sZ3Z3OGRlNzV4dDAzNG9sdmJ5YnpkdTF3azFpZiZlcD12MV9naWZzX3JlbGF0ZWQmY3Q9Zw/hxZMzujlY2Jv5sD36g/giphy.gif",
        "name": "Solo Swag",
        "rarity": "legendary",
    },
    {
        "url": "https://media.giphy.com/media/iiCQrGn7lEiWXF7fxe/giphy.gif",
        "name": "Rusdi  nah ini",
        "rarity": "legendary",
    },
    {
        "url": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3k4Y2ltd2J5bnA4dWNsNDQ1eWx5emJ1Zmp4bmkzemkycTdubzFpdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kMKvXRK36RijLVaaJb/giphy.gif",
        "name": "Rusdi Informasi Palsu",
        "rarity": "legendary",
    },
    # --- Mythic 🔴 ---
    {
        "url": "https://cdn.discordapp.com/attachments/1224139598255624252/1466400312376950926/RGB.gif?ex=69fe76f6&is=69fd2576&hm=77494915c3546f97f96c0f56c0f15c9a7bf94b92563a1c09cdc0343fab4c1c46",
        "name": "RGB Jomok",
        "rarity": "mythic",
    },
]
