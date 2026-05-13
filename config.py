"""Bot configuration: trigger word, GIF card pool, and rarity system."""

from __future__ import annotations

TRIGGER_WORD: str = "idy"

RARITY_CONFIG: dict = {
    "common":    {"emoji": "⚪", "color": 0x95a5a6, "label": "Common",    "shout": "Dapet kartu...",           "weight": 50},
    "rare":      {"emoji": "🔵", "color": 0x3498db, "label": "Rare",      "shout": "✨ Rare Pull!",            "weight": 25},
    "epic":      {"emoji": "🟣", "color": 0x9b59b6, "label": "Epic",      "shout": "🌟 EPIC PULL!",           "weight": 15},
    "legendary": {"emoji": "🟡", "color": 0xf1c40f, "label": "Legendary", "shout": "💫 LEGENDARY!!!",         "weight":  8},
    "mythic":    {"emoji": "🔴", "color": 0xe74c3c, "label": "MYTHIC",    "shout": "🔥 MYTHIC!!!! 🔥",        "weight":  2},
    "special":   {"emoji": "💚", "color": 0x2ecc71, "label": "SPECIAL",   "shout": "💚 S P E C I A L !!!! 💚", "weight":  0},
}

CARDS: list[dict] = [
    # --- Common ⚪ ---
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODQ2OGRwcWxxMW53bWJwMW5seXRvY281N3E2OWtscGRkYnd4cjhlMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TPURLKJjqYNyjb4Q2K/giphy.gif",
        "name": "Halah Nyocot",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODQ2OGRwcWxxMW53bWJwMW5seXRvY281N3E2OWtscGRkYnd4cjhlMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wgQTGjJMReIsbLnB3G/giphy.gif",
        "name": "Pura-pura ga liat",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3N2xvejd3ZHF6Yms1d3V0NWR1Z2IzMHdnNXA3eTljZTl4c3RsNG13YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/VBcO3pX9s9rs5H29DD/giphy.gif",
        "name": "Ngabuburit yuk",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3emYyNW9maWtheXV5ZjI2MXhxZnpkeGR6dXltdmptcnRyeWQ1b2RmdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/anec64aGGWj3KZ1iP4/giphy.gif",
        "name": "Malas Banget",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZWhrNDc0NTc4b3pvZXdsNDBmM3FuZjRiM2FhemViZjI3MDE5MTJ1NCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xjB29zEPeUogVR9Hha/giphy.gif",
        "name": "Nguwawor",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/Ihx6bbytRTEiQ7e4xF/giphy.gif",
        "name": "Andriana PSHT",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/jsLf2ALAjO8g7mpmt0/giphy.gif",
        "name": "Tolong dijelaskan",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/5PSwLEcp5qvlFtGasw/giphy.gif",
        "name": "Pegi Kau Suki",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzBhMDQ4ZnZ3ZXFnMWxwYjE4eGVibjUydnlvdjVpeHBzcW5nbzdmbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/D5LIdoJaeUBIfJC1sj/giphy.gif",
        "name": "Lebaran",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExanM4YXVyY2MzdzFlNWxhbHhndXU4eTcxdjd0MjJ1N3YzYjFibjVmaiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/uizHrLgtExbmXRtPhp/giphy.gif",
        "name": "Bohong",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNG5udGJ5bGdmbG83dzByNWlnN24xN2p6c2F0MXZuNmUwb2gxYzRrYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/iadQidGpB8molTjslq/giphy.gif",
        "name": "Selamat Berbuka",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXpmeGtoN2FkdzlzeDBtdnlkeW1udmV6N3dkaXlhMzBnaHZhYnQ2aSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6hEkOjy76BpkNG3K4p/giphy.gif",
        "name": "Admin Telah Tiba",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHN2MHZ4OXpsN3FwdzY2OG94cDdvd216NHJ0emduc3d3bGdoZGxndiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OUEkBHoiAzcAPDUHo9/giphy.gif",
        "name": "Rusdi Kapan yh",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bHg0djFjcHhhYzZnYzZydDkzNDhqdDZ1eXJxY2ZlemNqZHUxOGo3ayZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FHUq34j8vRBVS01uSj/giphy.gif",
        "name": "My Bini",
        "rarity": "common",
        "power": 100,
    },
    # --- Rare 🔵 ---
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503411763708821574/20231228_121857.jpg?ex=6a0340d0&is=6a01ef50&hm=f688750645b474c61cbf1d72e0d9b8ff1680361300e256287848e891d3c9fde2&=&format=webp&width=856&height=856",
        "name": "Bertolak Belakang",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503411765927477328/403857969_863969445206569_2607206982726272483_n.jpg?ex=6a0340d1&is=6a01ef51&hm=d9d3a5332d0413e55a55ee0092868d94f38c750f327d244b20fb55e2558c33a3&=&format=webp",
        "name": "Bercyanda",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503411779689119774/20077647deaae862fa5b259b6772f41f.jpg?ex=6a0340d4&is=6a01ef54&hm=997d236138d17d543d36fc75222f37ff51822b98ae7f972824e7d793b7df69c1&=&format=webp",
        "name": "Bodo Amat",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503408211427065876/FB_IMG_1703546913367.jpg?ex=6a033d81&is=6a01ec01&hm=64b0a12f2aa9700ba1d0dadc94d88c3b67cf58c82aff09475a5c4a8bb09b9963&=&format=webp",
        "name": "Laba-laba Sunda",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://images-ext-1.discordapp.net/external/Dd-z3ontuClF8E86MQhtdFZ0jCy6mGdHfZTZc0Dk7p8/https/i.pinimg.com/474x/70/68/b2/7068b215a3b47573850c3d0d82536e2b.jpg?format=webp",
        "name": "Spongebob Tuff",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGdwc3NlOWRndG90bm54c2VhanFscGJheWV5dG9nZzI2NGNyd25lYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H7oe4YDsrMbNuzCF1g/giphy.gif",
        "name": "Idy Dame yo",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xz0qNZfJM3XeKznwVq/giphy.gif",
        "name": "Malas",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTExdG9tNDd2cHVyMmQ3YjY5N3k0YXZ2OWc1MW5rajYzZ3hyM2s0ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3VUZmlLh5uPJRR12a4/giphy.gif",
        "name": "Pak Cik Peduli?",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502360650939236442/Fr8xtY1aIAEactb.png?ex=69ff6de3&is=69fe1c63&hm=464fc3298d0c8e313e5a231945dd7f15f51382c1ac2f84b95ea9e55dc06f2adf&=&format=webp&quality=lossless",
        "name": "Sengaja Ya Buat Aku Marah",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.discordapp.net/attachments/1092800373640675368/1210145536494018570/lv_0_20230605193804.gif?ex=6a0045db&is=69fef45b&hm=a7840e07926583e92d23aa8787915f3ac79a5ba80784ca68c912267d55e36c14&=",
        "name": "Gelombang Laut",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnloa2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9oryRGyTdzzFEBUgcb/giphy.gif",
        "name": "Amba Menangis",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.giphy.com/media/VwNySHxfzhksbDnR0v/giphy.gif",
        "name": "Mana Buktinya",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.giphy.com/media/gNjSEUHYeGVAiSRwyt/giphy.gif",
        "name": "Pilot Amba",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1501879984283717684/Screenshot_20260507_163251_TikTok.png?ex=69fe56fb&is=69fd057b&hm=41dca3836e6d370cdf6ac69e6c8c105f073bc9fa8d27b4b6d0d597dc475b67bb&=&format=webp&quality=lossless",
        "name": "Rewel Cipok",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzg2bDF4Y2NscXNscm5pZDhsbmdhbmwxanBscTN5dnkxZGhyNmR2MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9x8jtSVcUg6jmDzyk6/giphy.gif",
        "name": "Bobok",
        "rarity": "rare",
        "power": 250,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzg2bDF4Y2NscXNscm5pZDhsbmdhbmwxanBscTN5dnkxZGhyNmR2MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PROl6AeJzqAWo3n0Y8/giphy.gif",
        "name": "Ayah Tidur",
        "rarity": "rare",
        "power": 250,
    },
    # --- Epic 🟣 ---
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503411783057281235/20231003_022337.jpg?ex=6a0340d5&is=6a01ef55&hm=9273401c6c82a09a757a748b4199f44bb31c13b71d65c8f5057106746b87bc30&=&format=webp&width=1512&height=856",
        "name": "Sodara",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503408211896832170/456311363_1557874248491360_5963625286855722935_n.jpg?ex=6a033d81&is=6a01ec01&hm=8ea5623b03744febb10b4d3b653cd8de0f4cd062447be068af3592da492a2040&=&format=webp",
        "name": "Kenapa?",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.discordapp.net/attachments/854900758713073686/1503262835097079988/20260511_120716.jpg?ex=6a02b61d&is=6a01649d&hm=6bc6de35e32b58192516ed3f28da148ed709a31bad6e3b9796dbeae0a08c680d&=&format=webp",
        "name": "Rusdi Balon",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dnR5OGp4ejB6Ymh6Z2szMnU2NHNoMzRveGlvZW5rMWgyZDZkcnY5ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/eKwa7OVMk0Cqx8g8b5/giphy.gif",
        "name": "Mahkota Mu King",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502363686222696498/images.png?ex=69ff70b7&is=69fe1f37&hm=b3aadce74b720f64f3a1df54d1e085a3cc9d811961b93b90b1f23e39aba2d00b&=&format=webp&quality=lossless",
        "name": "Owo Swag",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NWtweWxrZ200Y3ljM3Rnc3E4enBjbmVmYTZrdW5qcXU3cHoxczBpdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zJi5F4LxaFEGBGlb9h/giphy.gif",
        "name": "Menggugah Selera",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGF6OHZtbzBlMGttbGswMDJkYmFwbXozMW1ydHZncGhra2F6aTRhbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dgWteQuo1LXqlxiDJU/giphy.gif",
        "name": "Solo Baca Buku",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnlva2g3Z3BpcWo5ZnA5dW9wenR1NmNpY2N3NjNvOHdrZGppdHhhMiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QGyYIduiYf1zUkFHfR/giphy.gif",
        "name": "Ape pula bodoh nih",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.giphy.com/media/bTnjjJn4pJLFUa0CLP/giphy.gif",
        "name": "Tertawa Tapi Teluka",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTIzd3lxbzUyejZvOGllb2Rwa3diaDQ2YWVtN28zaWUxYnN0amQzYiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/4Ri3wZqFjICSMS75J0/giphy.gif",
        "name": "Terompet Pemanggil Pasukan",
        "rarity": "epic",
        "power": 450,
    },
    {
        "url": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN240dW9iMWU3MTM1amMxaHdhOWNzdHhhbm5hMmcyanJvcjg3NXhreiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XFzGF2ZoTjlKdKmaGf/giphy.gif",
        "name": "Owo Sigma",
        "rarity": "epic",
        "power": 450,
    },
    # --- Legendary 🟡 ---
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503411783699005470/20231228_121847.jpg?ex=6a0340d5&is=6a01ef55&hm=4b4629b78608aff7172585e2a4affafdd8dbb9c1bdc5eb68a501e6159a2a55f0&=&format=webp",
        "name": "Toyota Supra 2000HP BRAkTAKTAK",
        "rarity": "legendary",
        "power": 700,
    },
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503408212253212762/244433a305a15c1c98f5068f3d63500f.jpg?ex=6a033d81&is=6a01ec01&hm=9b568fa4d9c602df08dd62c097971de8e36896bfe547da8822c830af6b1ea37a&=&format=webp",
        "name": "Merah",
        "rarity": "legendary",
        "power": 700,
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502367899938066503/tirai_emas.gif?ex=69ff74a3&is=69fe2323&hm=0c00be9160f114e8b6496044afa7c09de292045f834c9625e88bf14c6d8a42cb&=",
        "name": "Tirai Misterius",
        "rarity": "legendary",
        "power": 700,
    },

    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnYwMjQxN2RpYm1sZ3Z3OGRlNzV4dDAzNG9sdmJ5YnpkdTF3azFpZiZlcD12MV9naWZzX3JlbGF0ZWQmY3Q9Zw/hxZMzujlY2Jv5sD36g/giphy.gif",
        "name": "Solo Swag",
        "rarity": "legendary",
        "power": 700,
    },
    {
        "url": "https://media.giphy.com/media/iiCQrGn7lEiWXF7fxe/giphy.gif",
        "name": "Rusdi  nah ini",
        "rarity": "legendary",
        "power": 700,
    },
    {
        "url": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3k4Y2ltd2J5bnA4dWNsNDQ1eWx5emJ1Zmp4bmkzemkycTdubzFpdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kMKvXRK36RijLVaaJb/giphy.gif",
        "name": "Rusdi Informasi Palsu",
        "rarity": "legendary",
        "power": 700,
    },
    {
        "url": "https://media.discordapp.net/attachments/1297579892254441482/1465496007193133207/STK-20250602-WA0073.webp?ex=6a0072c3&is=69ff2143&hm=1df2040e901fb681dcb7296987b2bedb72b56034a452434c23cf65b9626c6bea&=&animated=true",
        "name": "Dimas Ketoprak",
        "rarity": "legendary",
        "power": 700,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXBzdXpqMDlpb3BoamtwMTFxN3hsaHc4cDNxc2dmYnY1amgxanljdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zLnmKwL1QQ9YbmAGJg/giphy.gif",
        "name": "King Ronaldo",
        "rarity": "legendary",
        "power": 700,
    },
    # --- Common ⚪ (extra) ---
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502362384562393138/1e9cc19e8ab2ae01baa1c70ca3a0012d.png?ex=69ff6f81&is=69fe1e01&hm=6352cee0657bb0cf3ecc69be37209f218534f9bf782d0489fea5b3b05060cd36&=&format=webp&quality=lossless",
        "name": "Rusdi Alamak",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502359668599816444/image.png?ex=6a0015b9&is=69fec439&hm=ba6084832b69bcb7ee5c1ec2eb17d246e2896c888d98f14e8122bf7dc989b012&=&format=webp&quality=lossless",
        "name": "Captain Amba",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2Z2eGtyZ2xncWhydzZ0bjJ5ZTNsdmlmYW9lNXllNjBhdDB4dTd6dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/v4kme8Y5rLzrKmZd6t/giphy.gif",
        "name": "SHSC PSHT",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcWcyd3hidTd0MW5lcmYybGo0cXZzdnJqMGpkdHliNXR5eDg4N2FocCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/NZf1ETC4H1HNJouNt1/giphy.gif",
        "name": "Kewer-Kewer Sopan",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXBzdXpqMDlpb3BoamtwMTFxN3hsaHc4cDNxc2dmYnY1amgxanljdSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/HQX3sliPpoxkcuOKiL/giphy.gif",
        "name": "Yes King",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTc1MjFneGcybDFueTZ1cHMweWRtOGlyaXNwbjk0dm9hZmhzeXp5YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2NVFMngAeelJvabc9W/giphy.gif",
        "name": "Ladesh Pelatihan Ketat",
        "rarity": "common",
        "power": 100,
    },
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502694339296628776/Screenshot_20260509_222902_TikTok.jpg?ex=6a00a4a9&is=69ff5329&hm=04beb41a44a028780e050dd4407128669bbd0b16face711f0db4c8694deee967&=&format=webp",
        "name": "Amba Gua Lagi Yang Kena",
        "rarity": "common",
        "power": 100,
    },
    # --- Mythic 🔴 ---
    {
        "url": "https://media.discordapp.net/attachments/640554506525868082/1502360275846692914/image.png?ex=69ff6d8a&is=69fe1c0a&hm=6b34444d76c10cb5b2ad6a536e9de2472f8d35176cdc022ac932bf8dfe347975&=&format=webp&quality=lossless",
        "name": "Ayam Madu Panggang",
        "rarity": "mythic",
        "power": 900,
    },
    {
        "url": "https://media.discordapp.net/attachments/980988443708522518/1447968945771646977/Messenger_creation_3A6D65A9-00EC-44BB-9E93-00112779E044.gif?ex=69ff4eaa&is=69fdfd2a&hm=8474396943f02e08c4815948390ead0e73a56aef68c3c065b1db20ef3539402a&=",
        "name": "Geol-geol",
        "rarity": "mythic",
        "power": 900,
    },
    {
        "url": "https://media.discordapp.net/attachments/1224139598255624252/1466400312376950926/RGB.gif?ex=6a007136&is=69ff1fb6&hm=ea4cb5e8fe93b5932a6f7d55fde24101af37857bb48d5213e120c60e46aa4c98&",
        "name": "Linggis RGB",
        "rarity": "mythic",
        "power": 900,
    },
    {
        "url": "https://media.discordapp.net/attachments/1131416137259819088/1502189723630698536/GettyImages-1340129852.webp?ex=69feceb3&is=69fd7d33&hm=33dfcedd5b106e70de81d6f98224b61d4220365bf5fa01a3721f23e4d844d4a9&=&format=webp&width=519&height=779",
        "name": "Gold Lil Nas",
        "rarity": "mythic",
        "power": 900,
    },
    # --- Special 💚 ---
    {
        "url": "https://media.discordapp.net/attachments/706813419705335920/1503960840884322416/images.jpg?ex=6a05402e&is=6a03eeae&hm=54311d99393e0bd9bafe899e8dc0d80a6818b8abf7294c765c9c0b1be71a5470&=&format=webp&width=281&height=280",
        "name": "Jesu Ankle Break",
        "rarity": "special",
        "power": 9999,
    },
]
