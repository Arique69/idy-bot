"""Discord bot that responds with a gacha card pull when the trigger word is detected."""

from __future__ import annotations

import logging
import random
import re
import sys
import time
from datetime import datetime, timezone

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv
import os

from config import CARDS, RARITY_CONFIG, TRIGGER_WORD
from data import load_data, save_data, get_user

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

_TRIGGER_PATTERN: re.Pattern[str] = re.compile(
    rf"\b{re.escape(TRIGGER_WORD)}\b", re.IGNORECASE
)

COOLDOWN_SECONDS = 30
_cooldowns: dict[int, float] = {}

RARITY_ORDER = ["common", "rare", "epic", "legendary", "mythic"]


def pull_card(user_id: int) -> tuple[dict, bool]:
    data = load_data()
    user = get_user(data, str(user_id))

    streak = user["common_streak"]
    is_pity = streak >= 3

    if is_pity:
        pity_rarities = [r for r in RARITY_CONFIG if r != "common" and any(c["rarity"] == r for c in CARDS)]
        weights = [RARITY_CONFIG[r]["weight"] for r in pity_rarities]
        chosen_rarity = random.choices(pity_rarities, weights=weights, k=1)[0]
        user["common_streak"] = 0
    else:
        rarities = list(RARITY_CONFIG.keys())
        weights = [RARITY_CONFIG[r]["weight"] for r in rarities]
        chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
        if chosen_rarity == "common":
            user["common_streak"] = streak + 1
        else:
            user["common_streak"] = 0

    pool = [c for c in CARDS if c["rarity"] == chosen_rarity]
    if not pool:
        pool = CARDS
    card = random.choice(pool)

    if card["name"] not in user["collection"]:
        user["collection"].append(card["name"])

    if chosen_rarity == "legendary":
        user["legendary_count"] += 1
    elif chosen_rarity == "mythic":
        user["mythic_count"] += 1

    save_data(data)
    return card, is_pity


def pull_card_simple() -> dict:
    """Pull a card without affecting user data (for duel)."""
    rarities = list(RARITY_CONFIG.keys())
    weights = [RARITY_CONFIG[r]["weight"] for r in rarities]
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
    pool = [c for c in CARDS if c["rarity"] == chosen_rarity]
    if not pool:
        pool = CARDS
    return random.choice(pool)


def contains_trigger(text: str) -> bool:
    return bool(_TRIGGER_PATTERN.search(text))


def _log_trigger(message: discord.Message) -> None:
    guild = message.guild.name if message.guild else "DM"
    channel = getattr(message.channel, "name", str(message.channel.id))
    user = str(message.author)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log.info("Trigger | %s | guild=%s channel=#%s user=%s", ts, guild, channel, user)


class TradeView(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member, card_a: str, card_b: str) -> None:
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.card_a = card_a
        self.card_b = card_b
        self.message: discord.Message | None = None

    async def _finish(self, interaction: discord.Interaction, content: str) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore
        await interaction.response.edit_message(content=content, view=self)
        self.stop()

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Bukan kamu yang diajak trade!", ephemeral=True)
            return

        data = load_data()
        user_a = get_user(data, str(self.challenger.id))
        user_b = get_user(data, str(self.target.id))

        if self.card_a not in user_a["collection"]:
            await self._finish(interaction, f"❌ Trade gagal — **{self.challenger.display_name}** udah ga punya **{self.card_a}**.")
            return
        if self.card_b not in user_b["collection"]:
            await self._finish(interaction, f"❌ Trade gagal — **{self.target.display_name}** udah ga punya **{self.card_b}**.")
            return

        user_a["collection"].remove(self.card_a)
        user_b["collection"].remove(self.card_b)
        if self.card_b not in user_a["collection"]:
            user_a["collection"].append(self.card_b)
        if self.card_a not in user_b["collection"]:
            user_b["collection"].append(self.card_a)

        save_data(data)
        await self._finish(
            interaction,
            f"✅ Trade berhasil!\n**{self.challenger.display_name}** dapat **{self.card_b}**\n**{self.target.display_name}** dapat **{self.card_a}**",
        )

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Bukan kamu yang diajak trade!", ephemeral=True)
            return
        await self._finish(interaction, f"❌ Trade ditolak oleh **{self.target.display_name}**.")

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore
        if self.message:
            await self.message.edit(content="⏰ Trade expired.", view=self)


def _build_card_embed(card: dict, is_pity: bool = False) -> discord.Embed:
    rarity = RARITY_CONFIG[card["rarity"]]
    embed = discord.Embed(
        title=rarity["shout"],
        description=f"{rarity['emoji']} **{card['name']}**\n`{rarity['label']}`",
        color=rarity["color"],
    )
    embed.set_image(url=card["url"])
    footer = "Idy Gacha System • ketik 'idy' buat pull lagi"
    if is_pity:
        footer = "🍀 Pity activated! • " + footer
    embed.set_footer(text=footer)
    return embed


class IdyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        @self.tree.command(name="cuaca", description="Cek cuaca hari ini di Jakarta")
        async def cuaca(interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://wttr.in/Jakarta?format=j1", timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        data = await resp.json(content_type=None)

                current = data["current_condition"][0]
                temp = current["temp_C"]
                feels_like = current["FeelsLikeC"]
                humidity = current["humidity"]
                wind = current["windspeedKmph"]
                desc = current["weatherDesc"][0]["value"]

                embed = discord.Embed(
                    title="Cuaca Jakarta Hari Ini",
                    color=discord.Color.blue(),
                )
                embed.add_field(name="Kondisi", value=desc, inline=False)
                embed.add_field(name="Suhu", value=f"{temp}°C (feels like {feels_like}°C)", inline=True)
                embed.add_field(name="Kelembapan", value=f"{humidity}%", inline=True)
                embed.add_field(name="Angin", value=f"{wind} km/h", inline=True)
                embed.set_footer(text="Sumber: wttr.in")

                await interaction.followup.send(embed=embed)

            except Exception as exc:
                log.error("Error fetching weather: %s", exc)
                await interaction.followup.send("Gagal ngambil data cuaca, coba lagi nanti.")

        @self.tree.command(name="leaderboard", description="Top 5 pemilik kartu legendary & mythic")
        async def leaderboard(interaction: discord.Interaction) -> None:
            data = load_data()
            users = data.get("users", {})

            ranked = sorted(
                users.items(),
                key=lambda x: x[1].get("legendary_count", 0) + x[1].get("mythic_count", 0),
                reverse=True,
            )[:5]

            if not ranked or all(u[1].get("legendary_count", 0) + u[1].get("mythic_count", 0) == 0 for u in ranked):
                await interaction.response.send_message("Belum ada yang dapet legendary atau mythic!")
                return

            embed = discord.Embed(title="🏆 Leaderboard Gacha", color=0xf1c40f)
            for i, (uid, udata) in enumerate(ranked, 1):
                legendary = udata.get("legendary_count", 0)
                mythic = udata.get("mythic_count", 0)
                if legendary + mythic == 0:
                    continue
                try:
                    fetched = await self.fetch_user(int(uid))
                    name = fetched.display_name
                except Exception:
                    name = f"User {uid}"
                embed.add_field(
                    name=f"{i}. {name}",
                    value=f"🟡 Legendary: {legendary}  🔴 Mythic: {mythic}",
                    inline=False,
                )

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="koleksi", description="Lihat koleksi kartu kamu")
        async def koleksi(interaction: discord.Interaction) -> None:
            data = load_data()
            user = get_user(data, str(interaction.user.id))
            collection = user.get("collection", [])

            if not collection:
                await interaction.response.send_message("Koleksi kamu masih kosong! Ketik `idy` buat pull.")
                return

            by_rarity: dict[str, list[str]] = {}
            for card_name in collection:
                card = next((c for c in CARDS if c["name"] == card_name), None)
                if card:
                    by_rarity.setdefault(card["rarity"], []).append(card_name)

            total_cards = len(CARDS)
            embed = discord.Embed(
                title=f"Koleksi {interaction.user.display_name}",
                description=f"Total: **{len(collection)}/{total_cards}** kartu unik",
                color=0x9b59b6,
            )
            for rarity in ["mythic", "legendary", "epic", "rare", "common"]:
                if rarity in by_rarity:
                    cfg = RARITY_CONFIG[rarity]
                    total_rarity = sum(1 for c in CARDS if c["rarity"] == rarity)
                    cards_str = "\n".join(f"• {name}" for name in by_rarity[rarity])
                    embed.add_field(
                        name=f"{cfg['emoji']} {cfg['label']} ({len(by_rarity[rarity])}/{total_rarity})",
                        value=cards_str,
                        inline=False,
                    )

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="saham", description="Cek harga saham (contoh: BBCA, TLKM, GOTO)")
        @app_commands.describe(ticker="Kode saham IDX (tanpa .JK) atau US (AAPL, TSLA, dll)")
        async def saham(interaction: discord.Interaction, ticker: str) -> None:
            await interaction.response.defer()
            try:
                ticker_upper = ticker.upper().strip()
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                }

                q = None
                async with aiohttp.ClientSession(headers=headers) as session:
                    for symbol in [f"{ticker_upper}.JK", ticker_upper]:
                        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            data = await resp.json(content_type=None)

                        chart = data.get("chart", {})
                        if chart.get("error") or not chart.get("result"):
                            continue

                        meta = chart["result"][0]["meta"]
                        price = meta.get("regularMarketPrice")
                        if price:
                            q = meta
                            q["_symbol"] = symbol
                            break

                if not q:
                    await interaction.followup.send(f"Saham `{ticker_upper}` tidak ditemukan. Cek kode sahamnya ya.")
                    return

                symbol = q["_symbol"]
                name = q.get("longName") or q.get("shortName") or symbol
                currency = q.get("currency", "")
                prev_close = q.get("previousClose") or q.get("chartPreviousClose", 0)
                change = price - prev_close if prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0
                high = q.get("regularMarketDayHigh")
                low = q.get("regularMarketDayLow")
                volume = q.get("regularMarketVolume")

                arrow = "🟢 ▲" if change >= 0 else "🔴 ▼"
                sign = "+" if change >= 0 else ""
                color = 0x2ecc71 if change >= 0 else 0xe74c3c

                embed = discord.Embed(title=f"{name} ({symbol})", color=color)
                embed.add_field(name="Harga", value=f"**{currency} {price:,.2f}**", inline=True)
                embed.add_field(name="Perubahan", value=f"{arrow} {sign}{change:,.2f} ({sign}{change_pct:.2f}%)", inline=True)
                embed.add_field(name="​", value="​", inline=True)
                embed.add_field(name="Tertinggi Hari Ini", value=f"{currency} {high:,.2f}" if high else "-", inline=True)
                embed.add_field(name="Terendah Hari Ini", value=f"{currency} {low:,.2f}" if low else "-", inline=True)
                embed.add_field(name="Volume", value=f"{volume:,}" if volume else "-", inline=True)
                embed.set_footer(text="Sumber: Yahoo Finance • Data bisa delay 15 menit")

                await interaction.followup.send(embed=embed)

            except Exception as exc:
                log.error("Error fetching stock %s: %s", ticker, exc)
                await interaction.followup.send("Gagal ngambil data saham, coba lagi nanti.")

        @self.tree.command(name="duel", description="Adu kartu sama user lain")
        @app_commands.describe(lawan="User yang mau diajak duel")
        async def duel(interaction: discord.Interaction, lawan: discord.Member) -> None:
            if lawan.bot:
                await interaction.response.send_message("Ga bisa duel sama bot!", ephemeral=True)
                return
            if lawan.id == interaction.user.id:
                await interaction.response.send_message("Ga bisa duel sama diri sendiri!", ephemeral=True)
                return

            card_a = pull_card_simple()
            card_b = pull_card_simple()

            rank_a = RARITY_ORDER.index(card_a["rarity"])
            rank_b = RARITY_ORDER.index(card_b["rarity"])

            cfg_a = RARITY_CONFIG[card_a["rarity"]]
            cfg_b = RARITY_CONFIG[card_b["rarity"]]

            if rank_a > rank_b:
                result = f"🏆 **{interaction.user.display_name}** menang!"
                color = 0x2ecc71
            elif rank_b > rank_a:
                result = f"🏆 **{lawan.display_name}** menang!"
                color = 0xe74c3c
            else:
                result = "🤝 **Seri!**"
                color = 0x95a5a6

            embed = discord.Embed(title="⚔️ DUEL KARTU!", description=result, color=color)
            embed.add_field(
                name=f"{interaction.user.display_name}",
                value=f"{cfg_a['emoji']} **{card_a['name']}**\n`{cfg_a['label']}`",
                inline=True,
            )
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(
                name=f"{lawan.display_name}",
                value=f"{cfg_b['emoji']} **{card_b['name']}**\n`{cfg_b['label']}`",
                inline=True,
            )
            embed.set_footer(text="Kartu duel tidak masuk koleksi")

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="kartu", description="Preview kartu tertentu")
        @app_commands.describe(nama="Nama kartu yang mau dilihat")
        async def kartu(interaction: discord.Interaction, nama: str) -> None:
            card = next((c for c in CARDS if c["name"].lower() == nama.lower()), None)
            if not card:
                await interaction.response.send_message(f"Kartu `{nama}` tidak ditemukan.", ephemeral=True)
                return

            rarity = RARITY_CONFIG[card["rarity"]]
            embed = discord.Embed(
                title=card["name"],
                description=f"{rarity['emoji']} `{rarity['label']}`",
                color=rarity["color"],
            )
            embed.set_image(url=card["url"])
            await interaction.response.send_message(embed=embed)

        @kartu.autocomplete("nama")
        async def kartu_autocomplete(interaction: discord.Interaction, current: str):
            matches = [
                app_commands.Choice(name=c["name"], value=c["name"])
                for c in CARDS
                if current.lower() in c["name"].lower()
            ]
            return matches[:25]

        @self.tree.command(name="trade", description="Tawarkan trade kartu ke user lain")
        @app_commands.describe(
            lawan="User yang mau diajak trade",
            kartu_kamu="Kartu kamu yang mau ditukar",
            kartu_dia="Kartu dia yang kamu mau",
        )
        async def trade(interaction: discord.Interaction, lawan: discord.Member, kartu_kamu: str, kartu_dia: str) -> None:
            if lawan.bot or lawan.id == interaction.user.id:
                await interaction.response.send_message("Ga bisa trade sama bot atau diri sendiri!", ephemeral=True)
                return

            data = load_data()
            user_a = get_user(data, str(interaction.user.id))
            user_b = get_user(data, str(lawan.id))

            if kartu_kamu not in user_a["collection"]:
                await interaction.response.send_message(f"Kamu ga punya kartu **{kartu_kamu}**!", ephemeral=True)
                return
            if kartu_dia not in user_b["collection"]:
                await interaction.response.send_message(f"**{lawan.display_name}** ga punya kartu **{kartu_dia}**!", ephemeral=True)
                return

            card_a = next((c for c in CARDS if c["name"] == kartu_kamu), None)
            card_b = next((c for c in CARDS if c["name"] == kartu_dia), None)
            cfg_a = RARITY_CONFIG[card_a["rarity"]] if card_a else {}
            cfg_b = RARITY_CONFIG[card_b["rarity"]] if card_b else {}

            view = TradeView(interaction.user, lawan, kartu_kamu, kartu_dia)
            embed = discord.Embed(
                title="🔄 Tawaran Trade",
                description=f"{lawan.mention}, **{interaction.user.display_name}** ngajak trade nih!",
                color=0x3498db,
            )
            embed.add_field(
                name=f"{interaction.user.display_name} kasih",
                value=f"{cfg_a.get('emoji', '')} **{kartu_kamu}**\n`{cfg_a.get('label', '')}`",
                inline=True,
            )
            embed.add_field(name="⇄", value="", inline=True)
            embed.add_field(
                name=f"{lawan.display_name} kasih",
                value=f"{cfg_b.get('emoji', '')} **{kartu_dia}**\n`{cfg_b.get('label', '')}`",
                inline=True,
            )
            embed.set_footer(text="Trade expire dalam 60 detik")

            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()

        @trade.autocomplete("kartu_kamu")
        async def trade_kartu_kamu_ac(interaction: discord.Interaction, current: str):
            data = load_data()
            user = get_user(data, str(interaction.user.id))
            return [
                app_commands.Choice(name=name, value=name)
                for name in user["collection"]
                if current.lower() in name.lower()
            ][:25]

        @trade.autocomplete("kartu_dia")
        async def trade_kartu_dia_ac(interaction: discord.Interaction, current: str):
            target = getattr(interaction.namespace, "lawan", None)
            if target:
                data = load_data()
                user = get_user(data, str(target.id))
                if user["collection"]:
                    return [
                        app_commands.Choice(name=name, value=name)
                        for name in user["collection"]
                        if current.lower() in name.lower()
                    ][:25]
            return [
                app_commands.Choice(name=c["name"], value=c["name"])
                for c in CARDS
                if current.lower() in c["name"].lower()
            ][:25]

        await self.tree.sync()
        log.info("Slash commands synced.")

    async def on_ready(self) -> None:
        log.info("Bot ready — logged in as %s (id=%s)", self.user, self.user.id)
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="Jomok Hepi",
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not contains_trigger(message.content):
            return

        now = time.time()
        last = _cooldowns.get(message.author.id, 0)
        remaining = COOLDOWN_SECONDS - (now - last)
        if remaining > 0:
            await message.reply(
                f"⏳ Cooldown! Tunggu **{remaining:.0f} detik** lagi.",
                mention_author=False,
                delete_after=5,
            )
            return

        _cooldowns[message.author.id] = now
        _log_trigger(message)

        card, is_pity = pull_card(message.author.id)
        embed = _build_card_embed(card, is_pity)
        log.info("Card pulled | %s | rarity=%s | pity=%s", card["name"], card["rarity"], is_pity)

        try:
            await message.reply(embed=embed, mention_author=False)
        except discord.Forbidden:
            log.warning(
                "Missing permission to send messages in channel %s", message.channel.id
            )
        except discord.HTTPException as exc:
            log.error("Discord API error when replying: %s", exc)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        log.critical(
            "DISCORD_TOKEN not set. Create a .env file with DISCORD_TOKEN=<your token>."
        )
        sys.exit(1)

    if not CARDS:
        log.critical("CARDS list in config.py is empty. Add at least one card.")
        sys.exit(1)

    intents = discord.Intents.default()
    intents.message_content = True

    client = IdyBot(intents=intents)

    try:
        client.run(token, log_handler=None)
    except discord.LoginFailure:
        log.critical("Invalid Discord token. Double-check your DISCORD_TOKEN in .env.")
        sys.exit(1)


if __name__ == "__main__":
    main()
