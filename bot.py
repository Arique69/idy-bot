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

COOLDOWN_SECONDS = 60
_cooldowns: dict[int, float] = {}

RARITY_ORDER = ["common", "rare", "epic", "legendary", "mythic"]

RARITY_NEXT = {
    "common": "rare",
    "rare": "epic",
    "epic": "legendary",
    "legendary": "mythic",
}

GUILD = discord.Object(id=490175609587105802)


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

    user["collection"][card["name"]] = user["collection"].get(card["name"], 0) + 1

    if chosen_rarity == "legendary":
        user["legendary_count"] += 1
    elif chosen_rarity == "mythic":
        user["mythic_count"] += 1

    save_data(data)
    return card, is_pity


def get_random_collection_card(user_id: int) -> dict | None:
    data = load_data()
    user = get_user(data, str(user_id))
    owned = [name for name, count in user.get("collection", {}).items() if count > 0]
    if not owned:
        return None
    card_name = random.choice(owned)
    return next((c for c in CARDS if c["name"] == card_name), None)


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

        if user_a["collection"].get(self.card_a, 0) < 1:
            await self._finish(interaction, f"❌ Trade gagal — **{self.challenger.display_name}** udah ga punya **{self.card_a}**.")
            return
        if user_b["collection"].get(self.card_b, 0) < 1:
            await self._finish(interaction, f"❌ Trade gagal — **{self.target.display_name}** udah ga punya **{self.card_b}**.")
            return

        user_a["collection"][self.card_a] -= 1
        if user_a["collection"][self.card_a] <= 0:
            del user_a["collection"][self.card_a]
        user_b["collection"][self.card_b] -= 1
        if user_b["collection"][self.card_b] <= 0:
            del user_b["collection"][self.card_b]
        user_a["collection"][self.card_b] = user_a["collection"].get(self.card_b, 0) + 1
        user_b["collection"][self.card_a] = user_b["collection"].get(self.card_a, 0) + 1

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


class DuelModal(discord.ui.Modal, title="Pilih Kartu Duel"):
    kartu_input = discord.ui.TextInput(
        label="Nama kartu yang mau kamu taruhkan",
        placeholder="Ketik nama kartu persis...",
        min_length=1,
        max_length=100,
    )

    def __init__(self, challenger: discord.Member, target: discord.Member, card_name_a: str, view: "DuelChallengeView") -> None:
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.card_name_a = card_name_a
        self.duel_view = view

    async def on_submit(self, interaction: discord.Interaction) -> None:
        card_name_b = self.kartu_input.value.strip()

        data = load_data()
        user_a = get_user(data, str(self.challenger.id))
        user_b = get_user(data, str(self.target.id))

        if user_a["collection"].get(self.card_name_a, 0) < 1:
            await interaction.response.edit_message(
                content=f"❌ Duel batal — **{self.challenger.display_name}** udah ga punya **{self.card_name_a}**.",
                embed=None, view=None,
            )
            self.duel_view.stop()
            return

        card_b = next((c for c in CARDS if c["name"].lower() == card_name_b.lower()), None)
        if not card_b:
            await interaction.response.send_message(
                f"Kartu **{card_name_b}** tidak ditemukan. Cek nama kartunya ya.", ephemeral=True
            )
            return

        real_name_b = card_b["name"]
        if user_b["collection"].get(real_name_b, 0) < 1:
            await interaction.response.send_message(
                f"Kamu ga punya kartu **{real_name_b}**!", ephemeral=True
            )
            return

        card_a = next((c for c in CARDS if c["name"] == self.card_name_a), None)
        rank_a = RARITY_ORDER.index(card_a["rarity"])
        rank_b = RARITY_ORDER.index(card_b["rarity"])
        cfg_a = RARITY_CONFIG[card_a["rarity"]]
        cfg_b = RARITY_CONFIG[card_b["rarity"]]

        gap = abs(rank_a - rank_b)
        if gap == 0:
            win_chance_a = 0.5
        else:
            win_chance_a = max(0.05, 0.5 - gap * 0.15) if rank_a > rank_b else min(0.95, 0.5 + gap * 0.15)

        challenger_wins = random.random() < win_chance_a

        if challenger_wins:
            winner, loser = self.challenger, self.target
            winner_gets, loser_loses = real_name_b, self.card_name_a
            result = f"🏆 **{self.challenger.display_name}** menang!"
            color = 0x2ecc71
        else:
            winner, loser = self.target, self.challenger
            winner_gets, loser_loses = self.card_name_a, real_name_b
            result = f"🏆 **{self.target.display_name}** menang!"
            color = 0xe74c3c

        pct_a = win_chance_a * 100
        pct_b = 100 - pct_a

        user_winner = get_user(data, str(winner.id))
        user_loser = get_user(data, str(loser.id))

        user_loser["collection"][loser_loses] -= 1
        if user_loser["collection"][loser_loses] <= 0:
            del user_loser["collection"][loser_loses]
        user_winner["collection"][winner_gets] = user_winner["collection"].get(winner_gets, 0) + 1

        user_winner["duel_wins"] = user_winner.get("duel_wins", 0) + 1
        user_loser["duel_losses"] = user_loser.get("duel_losses", 0) + 1

        card_won = next((c for c in CARDS if c["name"] == winner_gets), None)
        if card_won:
            if card_won["rarity"] == "legendary":
                user_winner["legendary_count"] = user_winner.get("legendary_count", 0) + 1
            elif card_won["rarity"] == "mythic":
                user_winner["mythic_count"] = user_winner.get("mythic_count", 0) + 1

        save_data(data)

        embed = discord.Embed(title="⚔️ HASIL DUEL!", description=result, color=color)
        embed.add_field(
            name=f"{self.challenger.display_name}",
            value=f"{cfg_a['emoji']} **{self.card_name_a}**\n`{cfg_a['label']}`\n🎲 {pct_a:.0f}%",
            inline=True,
        )
        embed.add_field(name="VS", value="⚔️", inline=True)
        embed.add_field(
            name=f"{self.target.display_name}",
            value=f"{cfg_b['emoji']} **{real_name_b}**\n`{cfg_b['label']}`\n🎲 {pct_b:.0f}%",
            inline=True,
        )
        embed.add_field(
            name="Perpindahan Kartu",
            value=f"**{winner.display_name}** mendapat **{winner_gets}** dari **{loser.display_name}**!",
            inline=False,
        )

        await interaction.response.edit_message(content=None, embed=embed, view=None)
        self.duel_view.stop()


class DuelChallengeView(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member, card_name_a: str) -> None:
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.card_name_a = card_name_a
        self.message: discord.Message | None = None

    @discord.ui.button(label="⚔️ Terima", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Bukan kamu yang ditantang!", ephemeral=True)
            return
        modal = DuelModal(self.challenger, self.target, self.card_name_a, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="❌ Tolak", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Bukan kamu yang ditantang!", ephemeral=True)
            return
        for item in self.children:
            item.disabled = True  # type: ignore
        await interaction.response.edit_message(
            content=f"❌ Duel ditolak oleh **{self.target.display_name}**.", embed=None, view=self
        )
        self.stop()

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore
        if self.message:
            await self.message.edit(content="⏰ Tantangan duel expired.", embed=None, view=self)


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

        @self.tree.command(name="rates", description="Lihat persentase drop rate tiap rarity")
        async def rates(interaction: discord.Interaction) -> None:
            total_weight = sum(r["weight"] for r in RARITY_CONFIG.values())
            embed = discord.Embed(title="🎴 Drop Rates", color=0x9b59b6)
            for rarity in ["mythic", "legendary", "epic", "rare", "common"]:
                cfg = RARITY_CONFIG[rarity]
                pct = cfg["weight"] / total_weight * 100
                card_count = sum(1 for c in CARDS if c["rarity"] == rarity)
                embed.add_field(
                    name=f"{cfg['emoji']} {cfg['label']}",
                    value=f"`{pct:.0f}%` — {card_count} kartu",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)

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
            collection = user.get("collection", {})

            if not collection:
                await interaction.response.send_message("Koleksi kamu masih kosong! Ketik `idy` buat pull.")
                return

            by_rarity: dict[str, list[tuple[str, int]]] = {}
            for card_name, count in collection.items():
                card = next((c for c in CARDS if c["name"] == card_name), None)
                if card:
                    by_rarity.setdefault(card["rarity"], []).append((card_name, count))

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
                    cards_str = "\n".join(
                        f"• {name} x{cnt}" if cnt > 1 else f"• {name}"
                        for name, cnt in by_rarity[rarity]
                    )
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

        @self.tree.command(name="duel", description="Adu kartu koleksi kamu — kartu yang kalah berpindah tangan!")
        @app_commands.describe(lawan="User yang mau diajak duel", kartu="Kartu kamu yang mau ditaruhkan")
        async def duel(interaction: discord.Interaction, lawan: discord.Member, kartu: str) -> None:
            if lawan.bot:
                await interaction.response.send_message("Ga bisa duel sama bot!", ephemeral=True)
                return
            if lawan.id == interaction.user.id:
                await interaction.response.send_message("Ga bisa duel sama diri sendiri!", ephemeral=True)
                return

            data = load_data()
            user_a = get_user(data, str(interaction.user.id))
            if user_a["collection"].get(kartu, 0) < 1:
                await interaction.response.send_message(f"Kamu ga punya kartu **{kartu}**!", ephemeral=True)
                return

            card_a = next((c for c in CARDS if c["name"] == kartu), None)
            if not card_a:
                await interaction.response.send_message(f"Kartu **{kartu}** tidak ditemukan.", ephemeral=True)
                return

            cfg_a = RARITY_CONFIG[card_a["rarity"]]

            view = DuelChallengeView(
                challenger=interaction.user,
                target=lawan,
                card_name_a=kartu,
            )
            embed = discord.Embed(
                title="⚔️ Tantangan Duel!",
                description=(
                    f"{lawan.mention}, **{interaction.user.display_name}** menantang kamu duel!\n\n"
                    f"Kalau kamu kalah, kartu kamu jadi milik dia — dan sebaliknya."
                ),
                color=0xe67e22,
            )
            embed.add_field(
                name=f"{interaction.user.display_name} taruh",
                value=f"{cfg_a['emoji']} **{kartu}**\n`{cfg_a['label']}`",
                inline=False,
            )
            embed.set_footer(text="Tantangan expire dalam 60 detik")

            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()

        @duel.autocomplete("kartu")
        async def duel_kartu_ac(interaction: discord.Interaction, current: str):
            data = load_data()
            user = get_user(data, str(interaction.user.id))
            return [
                app_commands.Choice(name=name, value=name)
                for name in user["collection"]
                if current.lower() in name.lower()
            ][:25]

        @self.tree.command(name="duelstats", description="Lihat statistik duel kamu atau user lain")
        @app_commands.describe(user="User yang mau dilihat statsnya (kosongkan untuk stats kamu sendiri)")
        async def duelstats(interaction: discord.Interaction, user: discord.Member = None) -> None:
            target = user or interaction.user
            data = load_data()
            udata = get_user(data, str(target.id))

            wins = udata.get("duel_wins", 0)
            losses = udata.get("duel_losses", 0)
            draws = udata.get("duel_draws", 0)
            total = wins + losses + draws
            winrate = (wins / total * 100) if total > 0 else 0

            embed = discord.Embed(
                title=f"⚔️ Duel Stats — {target.display_name}",
                color=0xf1c40f,
            )
            embed.add_field(name="🏆 Menang", value=str(wins), inline=True)
            embed.add_field(name="💀 Kalah", value=str(losses), inline=True)
            embed.add_field(name="🤝 Seri", value=str(draws), inline=True)
            embed.add_field(name="📊 Total Duel", value=str(total), inline=True)
            embed.add_field(name="📈 Win Rate", value=f"{winrate:.1f}%", inline=True)

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="duelleaderboard", description="Top 5 duelist dengan menang terbanyak")
        async def duelleaderboard(interaction: discord.Interaction) -> None:
            data = load_data()
            users = data.get("users", {})

            ranked = sorted(users.items(), key=lambda x: x[1].get("duel_wins", 0), reverse=True)[:5]

            if not ranked or all(u[1].get("duel_wins", 0) == 0 for u in ranked):
                await interaction.response.send_message("Belum ada yang pernah duel!")
                return

            embed = discord.Embed(title="⚔️ Duel Leaderboard", color=0xe74c3c)
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, (uid, ud) in enumerate(ranked):
                wins = ud.get("duel_wins", 0)
                losses = ud.get("duel_losses", 0)
                draws = ud.get("duel_draws", 0)
                if wins == 0:
                    continue
                try:
                    fetched = await self.fetch_user(int(uid))
                    name = fetched.display_name
                except Exception:
                    name = f"User {uid}"
                embed.add_field(
                    name=f"{medals[i]} {name}",
                    value=f"🏆 {wins} menang  💀 {losses} kalah  🤝 {draws} seri",
                    inline=False,
                )

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

            if user_a["collection"].get(kartu_kamu, 0) < 1:
                await interaction.response.send_message(f"Kamu ga punya kartu **{kartu_kamu}**!", ephemeral=True)
                return
            if user_b["collection"].get(kartu_dia, 0) < 1:
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

        @self.tree.command(name="gift", description="Kasih kartu duplikat ke user lain")
        @app_commands.describe(
            penerima="User yang mau dikasih kartu",
            kartu="Kartu duplikat yang mau dikasih (harus punya lebih dari 1)",
        )
        async def gift(interaction: discord.Interaction, penerima: discord.Member, kartu: str) -> None:
            if penerima.bot or penerima.id == interaction.user.id:
                await interaction.response.send_message("Ga bisa gift ke bot atau diri sendiri!", ephemeral=True)
                return

            data = load_data()
            sender = get_user(data, str(interaction.user.id))
            receiver = get_user(data, str(penerima.id))

            if sender["collection"].get(kartu, 0) < 2:
                await interaction.response.send_message(
                    f"Kamu ga punya duplikat **{kartu}**! Hanya kartu yang kamu punya lebih dari 1 yang bisa di-gift.",
                    ephemeral=True,
                )
                return

            sender["collection"][kartu] -= 1
            if sender["collection"][kartu] <= 0:
                del sender["collection"][kartu]
            receiver["collection"][kartu] = receiver["collection"].get(kartu, 0) + 1

            save_data(data)

            card_obj = next((c for c in CARDS if c["name"] == kartu), None)
            cfg = RARITY_CONFIG[card_obj["rarity"]] if card_obj else {}

            embed = discord.Embed(
                title="🎁 Gift Kartu!",
                description=f"**{interaction.user.display_name}** ngasih kartu ke {penerima.mention}!",
                color=cfg.get("color", 0x3498db),
            )
            embed.add_field(
                name="Kartu",
                value=f"{cfg.get('emoji', '')} **{kartu}**\n`{cfg.get('label', '')}`",
                inline=False,
            )
            await interaction.response.send_message(embed=embed)

        @gift.autocomplete("kartu")
        async def gift_kartu_ac(interaction: discord.Interaction, current: str):
            data = load_data()
            user = get_user(data, str(interaction.user.id))
            results = []
            for name, cnt in user["collection"].items():
                if cnt < 2 or current.lower() not in name.lower():
                    continue
                card_obj = next((c for c in CARDS if c["name"] == name), None)
                emoji = RARITY_CONFIG[card_obj["rarity"]]["emoji"] if card_obj else ""
                results.append(app_commands.Choice(name=f"{emoji} {name} (x{cnt})", value=name))
            return results[:25]

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
            if not pool:
                pool = CARDS
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

        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        log.info("Slash commands synced to guild %s.", GUILD.id)

    async def on_ready(self) -> None:
        log.info("Bot ready — logged in as %s (id=%s)", self.user, self.user.id)
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="Jomok Hepi",
        )
        await self.change_presence(activity=activity)
        channel = self.get_channel(854900758713073686)
        if channel:
            await channel.send("🔄 Bot updated and back online!")
            announce_file = "announce.txt"
            if os.path.exists(announce_file):
                with open(announce_file, "r", encoding="utf-8") as f:
                    announcement = f.read().strip()
                if announcement:
                    await channel.send(f"📢 **Update:**\n{announcement}")
                os.remove(announce_file)

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
