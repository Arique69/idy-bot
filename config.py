"""Bot configuration: trigger word, GIF card pool, and rarity system."""

from __future__ import annotations

TRIGGER_WORD: str = "idy"

RARITY_CONFIG: dict = {
    "common":    {"emoji": "⚪", "color": 0x95a5a6, "label": "Common",    "shout": "Dapet kartu...",    "weight": 50},
    "rare":      {"emoji": "🔵", "color": 0x3498db, "label": "Rare",      "shout": "✨ Rare Pull!",     "weight": 25},
    "epic":      {"emoji": "🟣", "color": 0x9b59b6, "label": "Epic",      "shout": "🌟 EPIC PULL!",    "weight": 15},
    "legendary": {"emoji": "🟡", "color": 0xf1c40f, "label": "Legendary", "shout": "💫 LEGENDARY!!!",  "weight":  8},
    "mythic":    {"emoji": "🔴", "color": 0xe74c3c, "label": "MYTHIC",    "shout": "🔥 MYTHIC!!!! 🔥", "weight":  2},
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
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHN2MHZ4OXpsN3FwdzY2OG94cDdvd216NHJ0emduc3d3bGdoZGxndiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OUEkBHoiAzcAPDUHo9/giphy.gif",
        "name": "Rusdi Kapan yh",
        "rarity": "common",
    },
    # --- Rare 🔵 ---
    {
        "url": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGdwc3NlOWRndG90bm54c2VhanFscGJheWV5dG9nZzI2NGNyd25lYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H7oe4YDsrMbNuzCF1g/giphy.gif",
        "name": "Idy Dame yo",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xz0qNZfJM3XeKznwVq/giphy.gif",
        "name": "Malas",
        "rarity": "rare",
    },
    {
        "url": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTExdG9tNDd2cHVyMmQ3YjY5N3k0YXZ2OWc1MW5rajYzZ3hyM2s0ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3VUZmlLh5uPJRR12a4/giphy.gif",
        "name": "Pak Cik Peduli?",
        "rarity": "rare",
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502360650939236442/Fr8xtY1aIAEactb.png?ex=69ff6de3&is=69fe1c63&hm=464fc3298d0c8e313e5a231945dd7f15f51382c1ac2f84b95ea9e55dc06f2adf&=&format=webp&quality=lossless",
        "name": "Sengaja Ya Buat Aku Marah",
        "rarity": "rare",
    },
    {
        "url": "https://tenor.com/view/brandon-barber-thug-thug-hunter-thug-shaker-barber-gif-25755953",
        "name": "Rusdi Hump Day",
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
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzg2bDF4Y2NscXNscm5pZDhsbmdhbmwxanBscTN5dnkxZGhyNmR2MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9x8jtSVcUg6jmDzyk6/giphy.gif",
        "name": "Bobok",
        "rarity": "rare",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzg2bDF4Y2NscXNscm5pZDhsbmdhbmwxanBscTN5dnkxZGhyNmR2MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PROl6AeJzqAWo3n0Y8/giphy.gif",
        "name": "Ayah Tidur",
        "rarity": "rare",
    },
    # --- Epic 🟣 ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dnR5OGp4ejB6Ymh6Z2szMnU2NHNoMzRveGlvZW5rMWgyZDZkcnY5ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/eKwa7OVMk0Cqx8g8b5/giphy.gif",
        "name": "Mahkota Mu King",
        "rarity": "epic",
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502363686222696498/images.png?ex=69ff70b7&is=69fe1f37&hm=b3aadce74b720f64f3a1df54d1e085a3cc9d811961b93b90b1f23e39aba2d00b&=&format=webp&quality=lossless",
        "name": "Owo Swag",
        "rarity": "epic",
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NWtweWxrZ200Y3ljM3Rnc3E4enBjbmVmYTZrdW5qcXU3cHoxczBpdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zJi5F4LxaFEGBGlb9h/giphy.gif",
        "name": "Menggugah Selera",
        "rarity": "epic",
    },
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
    # --- Common ⚪ (extra) ---
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502362384562393138/1e9cc19e8ab2ae01baa1c70ca3a0012d.png?ex=69ff6f81&is=69fe1e01&hm=6352cee0657bb0cf3ecc69be37209f218534f9bf782d0489fea5b3b05060cd36&=&format=webp&quality=lossless",
        "name": "Rusdi Alamak",
        "rarity": "common",
    },
    # --- Mythic 🔴 ---
    {
        "url": "https://media.discordapp.net/attachments/980988443708522518/1447968945771646977/Messenger_creation_3A6D65A9-00EC-44BB-9E93-00112779E044.gif?ex=69ff4eaa&is=69fdfd2a&hm=8474396943f02e08c4815948390ead0e73a56aef68c3c065b1db20ef3539402a&=",
        "name": "Geol-geol",
        "rarity": "mythic",
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502362704214622340/RGB.gif?ex=69ff6fcd&is=69fe1e4d&hm=94c5b515e756c016de41b4fd017d5c49b3347fb3dc275f6012937b7abb13a8b9&=",
        "name": "Linggis RGB",
        "rarity": "mythic",
    },
    {
        "url": "https://media.discordapp.net/attachments/1131416137259819088/1502189723630698536/GettyImages-1340129852.webp?ex=69feceb3&is=69fd7d33&hm=33dfcedd5b106e70de81d6f98224b61d4220365bf5fa01a3721f23e4d844d4a9&=&format=webp&width=519&height=779",
        "name": "Gold Lil Nas",
        "rarity": "mythic",
    },
]
