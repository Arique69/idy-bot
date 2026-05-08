"""Discord bot that responds with a gacha card pull when the trigger word is detected."""

from __future__ import annotations

import logging
import random
import re
import sys
from datetime import datetime, timezone

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv
import os

from config import CARDS, RARITY_CONFIG, TRIGGER_WORD

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


def pull_card() -> dict:
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


def _build_card_embed(card: dict) -> discord.Embed:
    rarity = RARITY_CONFIG[card["rarity"]]
    embed = discord.Embed(
        title=rarity["shout"],
        description=f"{rarity['emoji']} **{card['name']}**\n`{rarity['label']}`",
        color=rarity["color"],
    )
    embed.set_image(url=card["url"])
    embed.set_footer(text="Idy Gacha System • ketik 'idy' buat pull lagi")
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

        _log_trigger(message)

        card = pull_card()
        embed = _build_card_embed(card)
        log.info("Card pulled | %s | rarity=%s", card["name"], card["rarity"])

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
