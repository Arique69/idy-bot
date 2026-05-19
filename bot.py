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

from config import CARDS, RARITY_CONFIG, TRIGGER_WORD, ELEMENTS, ELEMENT_ADVANTAGES
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

RARITY_ORDER = ["common", "rare", "epic", "legendary", "mythic", "special"]


def compute_win_chance(card_a: dict, card_b: dict) -> tuple[float, bool]:
    """Returns (win_chance_for_a, misteri_dodged)."""
    rank_a = RARITY_ORDER.index(card_a["rarity"])
    rank_b = RARITY_ORDER.index(card_b["rarity"])
    gap = rank_a - rank_b
    base = 0.5 + gap * 0.15
    atk_mod = (card_a["atk"] - card_b["atk"]) / 200
    skill_a = card_a["skill"]["bonus"] if card_a.get("skill") else 0
    skill_b = card_b["skill"]["bonus"] if card_b.get("skill") else 0
    elem_a = card_a.get("element", "")
    elem_b = card_b.get("element", "")
    elem_mod = 0.0
    misteri_dodged = False
    if elem_b in ELEMENT_ADVANTAGES.get(elem_a, []):
        elem_mod += 0.05
    if elem_a in ELEMENT_ADVANTAGES.get(elem_b, []):
        if elem_a == "Misteri" and random.random() < 0.20:
            misteri_dodged = True
        else:
            elem_mod -= 0.05
    return max(0.05, min(0.95, base + atk_mod + skill_a - skill_b + elem_mod)), misteri_dodged


_FINISHERS_UNDERDOG = [
    "nobody told him he was supposed to lose",
    "the math was wrong actually",
    "chaos wins again",
    "this is why we play the game",
    "the odds filed a complaint",
    "science has no explanation for this",
    "probability left the server",
    "he didn't get the memo",
]

_FINISHERS_DOMINANT = [
    "as expected. moving on.",
    "this was never a competition",
    "called it.",
    "next.",
    "not even close",
    "the result was obvious before it started",
    "destiny was very clear about this one",
]

_FINISHERS_CLOSE = [
    "pure coin flip energy",
    "literally could have gone either way",
    "the universe decided",
    "a very serious and legitimate battle",
    "both tried. one tried slightly more.",
    "the margin was basically nothing",
    "extremely professional fight",
]

_FINISHERS_MISTERI = [
    "nobody knows how",
    "the curtain reveals nothing",
    "statistically this shouldn't happen",
    "even the winner looks confused",
    "no witnesses. no explanation.",
    "the mystery remains",
]

_FINISHERS_ELEMENT: dict[tuple[str, str], list[str]] = {
    ("Sigma", "Baper"):    ["emotions don't work on him", "he simply did not care", "unbothered. completely."],
    ("Baper", "Nyocot"):   ["the tears shut him up", "drama beats noise every time", "feelings > words"],
    ("Nyocot", "Ngantuk"): ["the nonstop talking woke him up", "you can't sleep through that", "words as an alarm clock"],
    ("Ngantuk", "Pejuang"):["too tired to even train today", "the warrior forgot to set an alarm", "sleep beats discipline"],
    ("Pejuang", "Sigma"):  ["grind has physical limits", "sigma met someone who actually trained", "real effort beats mindset"],
    ("Pejuang", "Lapar"):  ["training beats hunger today", "discipline overpowered the stomach", "the warrior ate before the fight"],
    ("Lapar", "Nyocot"):   ["hunger is louder than words", "he was too hungry to argue", "food motivation is real"],
    ("Lapar", "Baper"):    ["hunger overrides emotion", "no time to be sad when starving", "biological needs first"],
    ("Lapar", "Ngantuk"):  ["you can't sleep when you're this hungry", "hunger woke him up", "the stomach said no"],
    ("Rusdi", "Misteri"):  ["Rusdi always finds out", "no secret survives Rusdi", "the mystery was solved immediately"],
}


def get_finisher(
    win_chance_winner: float,
    elem_winner: str,
    elem_loser: str,
    misteri_dodged: bool,
) -> str:
    if misteri_dodged:
        return random.choice(_FINISHERS_MISTERI)
    matchup_lines = _FINISHERS_ELEMENT.get((elem_winner, elem_loser))
    if matchup_lines:
        return random.choice(matchup_lines)
    if win_chance_winner <= 0.30:
        return random.choice(_FINISHERS_UNDERDOG)
    if win_chance_winner >= 0.70:
        return random.choice(_FINISHERS_DOMINANT)
    return random.choice(_FINISHERS_CLOSE)


CLAIM_DATE = (2026, 5, 14)  # year, month, day

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


def pull_card_simple() -> dict:
    rarities = list(RARITY_CONFIG.keys())
    weights = [RARITY_CONFIG[r]["weight"] for r in rarities]
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
    pool = [c for c in CARDS if c["rarity"] == chosen_rarity]
    return random.choice(pool)


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
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return

        data = load_data()
        user_a = get_user(data, str(self.challenger.id))
        user_b = get_user(data, str(self.target.id))

        if user_a["collection"].get(self.card_a, 0) < 1:
            await self._finish(interaction, f"❌ Trade failed — **{self.challenger.display_name}** no longer has **{self.card_a}**.")
            return
        if user_b["collection"].get(self.card_b, 0) < 1:
            await self._finish(interaction, f"❌ Trade failed — **{self.target.display_name}** no longer has **{self.card_b}**.")
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
            f"✅ Trade complete!\n**{self.challenger.display_name}** got **{self.card_b}**\n**{self.target.display_name}** got **{self.card_a}**",
        )

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return
        await self._finish(interaction, f"❌ Trade declined by **{self.target.display_name}**.")

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore
        if self.message:
            await self.message.edit(content="⏰ Trade expired.", view=self)



def _build_card_embed(card: dict, is_pity: bool = False) -> discord.Embed:
    rarity = RARITY_CONFIG[card["rarity"]]
    elem = ELEMENTS.get(card.get("element", ""), None)
    elem_str = f" | {elem['emoji']} {elem['label']}" if elem else ""
    desc = f"{rarity['emoji']} **{card['name']}**\n`{rarity['label']}` | ⚔️ ATK {card['atk']}{elem_str}"
    if card.get("skill"):
        desc += f"\n✨ **{card['skill']['name']}** — {card['skill']['desc']}"
    embed = discord.Embed(
        title=rarity["shout"],
        description=desc,
        color=rarity["color"],
    )
    embed.set_image(url=card["url"])
    footer = "Idy Gacha System • type 'idy' to pull again"
    if is_pity:
        footer = "🍀 Pity activated! • " + footer
    embed.set_footer(text=footer)
    return embed


class IdyBot(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        @self.tree.command(name="cuaca", description="Check today's weather for any city")
        @app_commands.describe(city="City name (default: Jakarta)")
        async def cuaca(interaction: discord.Interaction, city: str = "Jakarta") -> None:
            await interaction.response.defer()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://wttr.in/{city}?format=j1", timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        data = await resp.json(content_type=None)

                if data.get("current_condition") is None:
                    await interaction.followup.send(f"City `{city}` not found.")
                    return

                current = data["current_condition"][0]
                area = data.get("nearest_area", [{}])[0]
                country = area.get("country", [{}])[0].get("value", "")
                temp = current["temp_C"]
                feels_like = current["FeelsLikeC"]
                humidity = current["humidity"]
                wind = current["windspeedKmph"]
                desc = current["weatherDesc"][0]["value"]

                embed = discord.Embed(
                    title=f"{city.title()}{', ' + country if country else ''} — Weather Today",
                    color=discord.Color.blue(),
                )
                embed.add_field(name="Condition", value=desc, inline=False)
                embed.add_field(name="Temperature", value=f"{temp}°C (feels like {feels_like}°C)", inline=True)
                embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
                embed.add_field(name="Wind", value=f"{wind} km/h", inline=True)
                embed.set_footer(text="Source: wttr.in")

                await interaction.followup.send(embed=embed)

            except Exception as exc:
                log.error("Error fetching weather: %s", exc)
                await interaction.followup.send("Failed to fetch weather data, try again later.")

        @self.tree.command(name="rates", description="View drop rate percentages per rarity")
        async def rates(interaction: discord.Interaction) -> None:
            total_weight = sum(r["weight"] for r in RARITY_CONFIG.values())
            embed = discord.Embed(title="🎴 Drop Rates", color=0x9b59b6)
            for rarity in ["mythic", "legendary", "epic", "rare", "common"]:
                cfg = RARITY_CONFIG[rarity]
                pct = cfg["weight"] / total_weight * 100
                card_count = sum(1 for c in CARDS if c["rarity"] == rarity)
                embed.add_field(
                    name=f"{cfg['emoji']} {cfg['label']}",
                    value=f"`{pct:.0f}%` — {card_count} cards",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="leaderboard", description="Top 5 players with the most legendary & mythic cards")
        async def leaderboard(interaction: discord.Interaction) -> None:
            data = load_data()
            users = data.get("users", {})

            ranked = sorted(
                users.items(),
                key=lambda x: x[1].get("legendary_count", 0) + x[1].get("mythic_count", 0),
                reverse=True,
            )[:5]

            if not ranked or all(u[1].get("legendary_count", 0) + u[1].get("mythic_count", 0) == 0 for u in ranked):
                await interaction.response.send_message("Nobody has pulled a legendary or mythic yet!")
                return

            embed = discord.Embed(title="🏆 Gacha Leaderboard", color=0xf1c40f)
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

        @self.tree.command(name="koleksi", description="View your card collection")
        async def koleksi(interaction: discord.Interaction) -> None:
            data = load_data()
            user = get_user(data, str(interaction.user.id))
            collection = user.get("collection", {})

            if not collection:
                await interaction.response.send_message("Your collection is empty! Type `idy` to pull a card.")
                return

            by_rarity: dict[str, list[tuple[str, int]]] = {}
            for card_name, count in collection.items():
                card = next((c for c in CARDS if c["name"] == card_name), None)
                if card:
                    by_rarity.setdefault(card["rarity"], []).append((card_name, count))

            total_cards = len(CARDS)
            owned_unique = sum(len(cards) for cards in by_rarity.values())
            embed = discord.Embed(
                title=f"{interaction.user.display_name}'s Collection",
                description=f"Total: **{owned_unique}/{total_cards}** unique cards",
                color=0x9b59b6,
            )
            for rarity in ["special", "mythic", "legendary", "epic", "rare", "common"]:
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

        @self.tree.command(name="saham", description="Check stock price (e.g. BBCA, TLKM, GOTO)")
        @app_commands.describe(ticker="IDX stock code (without .JK) or US ticker (AAPL, TSLA, etc)")
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
                    await interaction.followup.send(f"Stock `{ticker_upper}` not found. Check the ticker symbol.")
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
                embed.add_field(name="Price", value=f"**{currency} {price:,.2f}**", inline=True)
                embed.add_field(name="Change", value=f"{arrow} {sign}{change:,.2f} ({sign}{change_pct:.2f}%)", inline=True)
                embed.add_field(name="​", value="​", inline=True)
                embed.add_field(name="Day High", value=f"{currency} {high:,.2f}" if high else "-", inline=True)
                embed.add_field(name="Day Low", value=f"{currency} {low:,.2f}" if low else "-", inline=True)
                embed.add_field(name="Volume", value=f"{volume:,}" if volume else "-", inline=True)
                embed.set_footer(text="Source: Yahoo Finance • Data may be delayed 15 min")

                await interaction.followup.send(embed=embed)

            except Exception as exc:
                log.error("Error fetching stock %s: %s", ticker, exc, exc_info=True)
                await interaction.followup.send("Failed to fetch stock data, try again later.")

        @self.tree.command(name="duel", description="Challenge another user to a card duel")
        @app_commands.describe(lawan="User to duel")
        async def duel(interaction: discord.Interaction, lawan: discord.Member) -> None:
            if lawan.bot:
                await interaction.response.send_message("Can't duel a bot!", ephemeral=True)
                return
            if lawan.id == interaction.user.id:
                await interaction.response.send_message("Can't duel yourself!", ephemeral=True)
                return

            card_a = get_random_collection_card(interaction.user.id)
            if not card_a:
                await interaction.response.send_message("You don't have any cards!", ephemeral=True)
                return
            card_b = get_random_collection_card(lawan.id)
            if not card_b:
                await interaction.response.send_message(f"**{lawan.display_name}** doesn't have any cards!", ephemeral=True)
                return

            cfg_a = RARITY_CONFIG[card_a["rarity"]]
            cfg_b = RARITY_CONFIG[card_b["rarity"]]

            data = load_data()
            user_a = get_user(data, str(interaction.user.id))
            user_b = get_user(data, str(lawan.id))

            win_chance_a, misteri_dodged = compute_win_chance(card_a, card_b)
            a_wins = random.random() < win_chance_a

            if a_wins:
                result = f"🏆 **{interaction.user.display_name}** wins!"
                color = 0x2ecc71
                winner_card = card_a
                loser_card = card_b
                win_chance_winner = win_chance_a
                user_a["duel_wins"] = user_a.get("duel_wins", 0) + 1
                user_b["duel_losses"] = user_b.get("duel_losses", 0) + 1
            else:
                result = f"🏆 **{lawan.display_name}** wins!"
                color = 0xe74c3c
                winner_card = card_b
                loser_card = card_a
                win_chance_winner = 1 - win_chance_a
                user_b["duel_wins"] = user_b.get("duel_wins", 0) + 1
                user_a["duel_losses"] = user_a.get("duel_losses", 0) + 1

            save_data(data)

            finisher = get_finisher(
                win_chance_winner,
                winner_card.get("element", ""),
                loser_card.get("element", ""),
                misteri_dodged,
            )

            embed = discord.Embed(title="⚔️ CARD DUEL!", description=result, color=color)
            pct_a = win_chance_a * 100
            pct_b = 100 - pct_a

            def card_field(card, cfg, pct):
                elem = ELEMENTS.get(card.get("element", ""), None)
                elem_str = f" | {elem['emoji']} {elem['label']}" if elem else ""
                lines = [f"{cfg['emoji']} **{card['name']}**", f"`{cfg['label']}` | ⚔️ ATK {card['atk']}{elem_str}", f"🎲 {pct:.0f}%"]
                if card.get("skill"):
                    lines.append(f"✨ **{card['skill']['name']}** — {card['skill']['desc']} (+{card['skill']['bonus']*100:.0f}%)")
                return "\n".join(lines)

            embed.add_field(name=interaction.user.display_name, value=card_field(card_a, cfg_a, pct_a), inline=True)
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(name=lawan.display_name, value=card_field(card_b, cfg_b, pct_b), inline=True)
            embed.add_field(name="🃏 Winner Card", value=f"**{winner_card['name']}**", inline=False)
            embed.add_field(name="💬", value=f"*{finisher}*", inline=False)
            embed.set_image(url=winner_card["url"])

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="duelstats", description="View duel statistics for you or another user")
        @app_commands.describe(user="User to check stats for (leave empty for yourself)")
        async def duelstats(interaction: discord.Interaction, user: discord.Member = None) -> None:
            target = user or interaction.user
            data = load_data()
            udata = get_user(data, str(target.id))

            wins = udata.get("duel_wins", 0)
            losses = udata.get("duel_losses", 0)
            total = wins + losses
            winrate = (wins / total * 100) if total > 0 else 0

            embed = discord.Embed(
                title=f"⚔️ Duel Stats — {target.display_name}",
                color=0xf1c40f,
            )
            embed.add_field(name="🏆 Wins", value=str(wins), inline=True)
            embed.add_field(name="💀 Losses", value=str(losses), inline=True)
            embed.add_field(name="📊 Total Duels", value=str(total), inline=True)
            embed.add_field(name="📈 Win Rate", value=f"{winrate:.1f}%", inline=True)

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="duelleaderboard", description="Top 5 duelists with the most wins")
        async def duelleaderboard(interaction: discord.Interaction) -> None:
            data = load_data()
            users = data.get("users", {})

            ranked = sorted(users.items(), key=lambda x: x[1].get("duel_wins", 0), reverse=True)[:5]

            if not ranked or all(u[1].get("duel_wins", 0) == 0 for u in ranked):
                await interaction.response.send_message("Nobody has dueled yet!")
                return

            embed = discord.Embed(title="⚔️ Duel Leaderboard", color=0xe74c3c)
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, (uid, ud) in enumerate(ranked):
                wins = ud.get("duel_wins", 0)
                losses = ud.get("duel_losses", 0)
                if wins == 0:
                    continue
                try:
                    fetched = await self.fetch_user(int(uid))
                    name = fetched.display_name
                except Exception:
                    name = f"User {uid}"
                embed.add_field(
                    name=f"{medals[i]} {name}",
                    value=f"🏆 {wins} wins  💀 {losses} losses",
                    inline=False,
                )

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="kartu", description="Preview a specific card")
        @app_commands.describe(nama="Name of the card to preview")
        async def kartu(interaction: discord.Interaction, nama: str) -> None:
            card = next((c for c in CARDS if c["name"].lower() == nama.lower()), None)
            if not card:
                await interaction.response.send_message(f"Card `{nama}` not found.", ephemeral=True)
                return

            rarity = RARITY_CONFIG[card["rarity"]]
            elem = ELEMENTS.get(card.get("element", ""), None)
            elem_str = f" | {elem['emoji']} {elem['label']}" if elem else ""
            desc = f"{rarity['emoji']} `{rarity['label']}` | ⚔️ ATK {card['atk']}{elem_str}"
            if card.get("skill"):
                desc += f"\n✨ **{card['skill']['name']}** — {card['skill']['desc']} (+{card['skill']['bonus']*100:.0f}%)"
            embed = discord.Embed(
                title=card["name"],
                description=desc,
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

        @self.tree.command(name="trade", description="Offer a card trade to another user")
        @app_commands.describe(
            lawan="User to trade with",
            kartu_kamu="Your card to trade away",
            kartu_dia="Their card that you want",
        )
        async def trade(interaction: discord.Interaction, lawan: discord.Member, kartu_kamu: str, kartu_dia: str) -> None:
            if lawan.bot or lawan.id == interaction.user.id:
                await interaction.response.send_message("Can't trade with a bot or yourself!", ephemeral=True)
                return

            data = load_data()
            user_a = get_user(data, str(interaction.user.id))
            user_b = get_user(data, str(lawan.id))

            if user_a["collection"].get(kartu_kamu, 0) < 1:
                await interaction.response.send_message(f"You don't have **{kartu_kamu}**!", ephemeral=True)
                return
            if user_b["collection"].get(kartu_dia, 0) < 1:
                await interaction.response.send_message(f"**{lawan.display_name}** doesn't have **{kartu_dia}**!", ephemeral=True)
                return

            card_a = next((c for c in CARDS if c["name"] == kartu_kamu), None)
            card_b = next((c for c in CARDS if c["name"] == kartu_dia), None)
            cfg_a = RARITY_CONFIG[card_a["rarity"]] if card_a else {}
            cfg_b = RARITY_CONFIG[card_b["rarity"]] if card_b else {}

            view = TradeView(interaction.user, lawan, kartu_kamu, kartu_dia)
            embed = discord.Embed(
                title="🔄 Trade Offer",
                description=f"{lawan.mention}, **{interaction.user.display_name}** wants to trade!",
                color=0x3498db,
            )
            embed.add_field(
                name=f"{interaction.user.display_name} offers",
                value=f"{cfg_a.get('emoji', '')} **{kartu_kamu}**\n`{cfg_a.get('label', '')}`",
                inline=True,
            )
            embed.add_field(name="⇄", value="", inline=True)
            embed.add_field(
                name=f"{lawan.display_name} offers",
                value=f"{cfg_b.get('emoji', '')} **{kartu_dia}**\n`{cfg_b.get('label', '')}`",
                inline=True,
            )
            embed.set_footer(text="Trade expires in 60 seconds")

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

        @self.tree.command(name="gift", description="Give a duplicate card to another user")
        @app_commands.describe(
            penerima="User to give the card to",
            kartu="Duplicate card to give (must own more than 1)",
        )
        async def gift(interaction: discord.Interaction, penerima: discord.Member, kartu: str) -> None:
            if penerima.bot or penerima.id == interaction.user.id:
                await interaction.response.send_message("Can't gift to a bot or yourself!", ephemeral=True)
                return

            data = load_data()
            sender = get_user(data, str(interaction.user.id))
            receiver = get_user(data, str(penerima.id))

            if sender["collection"].get(kartu, 0) < 2:
                await interaction.response.send_message(
                    f"You don't have a duplicate of **{kartu}**! You need more than 1 copy to gift it.",
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
                title="🎁 Card Gift!",
                description=f"**{interaction.user.display_name}** gifted a card to {penerima.mention}!",
                color=cfg.get("color", 0x3498db),
            )
            embed.add_field(
                name="Card",
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

        @self.tree.command(name="claim", description="Claim the exclusive special card — only available on May 14 2026!")
        async def claim(interaction: discord.Interaction) -> None:
            today = datetime.now(timezone.utc)
            if (today.year, today.month, today.day) != CLAIM_DATE:
                await interaction.response.send_message(
                    "❌ This special card can only be claimed on **May 14, 2026**!", ephemeral=True
                )
                return

            special_card = next((c for c in CARDS if c["rarity"] == "special"), None)
            if not special_card:
                await interaction.response.send_message("Special card not found.", ephemeral=True)
                return

            data = load_data()
            user = get_user(data, str(interaction.user.id))

            if user.get("claimed_special"):
                await interaction.response.send_message(
                    "❌ You've already claimed this special card!", ephemeral=True
                )
                return

            user["collection"][special_card["name"]] = user["collection"].get(special_card["name"], 0) + 1
            user["claimed_special"] = True
            save_data(data)

            cfg = RARITY_CONFIG["special"]
            embed = discord.Embed(
                title=cfg["shout"],
                description=f"{cfg['emoji']} **{special_card['name']}**\n`{cfg['label']}`",
                color=cfg["color"],
            )
            embed.set_image(url=special_card["url"])
            embed.set_footer(text="Exclusive card May 14 2026 • Can only be claimed once!")
            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="merge", description="Merge 2 duplicate cards into a higher rarity card")
        @app_commands.describe(kartu="Card to merge (must own at least 3)")
        async def merge(interaction: discord.Interaction, kartu: str) -> None:
            data = load_data()
            user = get_user(data, str(interaction.user.id))

            card_obj = next((c for c in CARDS if c["name"] == kartu), None)
            if card_obj is None or user["collection"].get(kartu, 0) < 3:
                await interaction.response.send_message(
                    f"You need at least 3 copies of **{kartu}** to merge!", ephemeral=True
                )
                return

            if card_obj["rarity"] == "mythic":
                await interaction.response.send_message(
                    "Mythic is the highest rarity, can't merge further!", ephemeral=True
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
                title="🔀 Cards Merged",
                description=f"{src_cfg['emoji']} **{kartu}** x2\n`{src_cfg['label']}`",
                color=src_cfg["color"],
            )
            embed_src.set_image(url=card_obj["url"])

            embed_res = discord.Embed(
                title="✨ Evolution Result!",
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
                f"⏳ Cooldown! Wait **{remaining:.0f}s** more.",
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
