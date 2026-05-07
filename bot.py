"""Discord bot that responds with a GIF when the trigger word is detected."""

import logging
import random
import re
import sys
from datetime import datetime, timezone

import discord
from dotenv import load_dotenv
import os

from config import GIFS, TRIGGER_WORD

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# Pre-compile the trigger pattern: whole-word, case-insensitive
_TRIGGER_PATTERN: re.Pattern[str] = re.compile(
    rf"\b{re.escape(TRIGGER_WORD)}\b", re.IGNORECASE
)


def pick_gif() -> str:
    """Return a random GIF URL from the configured pool."""
    return random.choice(GIFS)


def contains_trigger(text: str) -> bool:
    """Return True if *text* contains the trigger word as a whole word."""
    return bool(_TRIGGER_PATTERN.search(text))


def _log_trigger(message: discord.Message) -> None:
    """Log a trigger event without recording message content."""
    guild = message.guild.name if message.guild else "DM"
    channel = getattr(message.channel, "name", str(message.channel.id))
    user = f"{message.author.name}#{message.author.discriminator}"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log.info("Trigger | %s | guild=%s channel=#%s user=%s", ts, guild, channel, user)


class IdyBot(discord.Client):
    """Client subclass that listens for the trigger word and replies with a GIF."""

    async def on_ready(self) -> None:
        """Called when the bot has connected and is ready."""
        log.info("Bot ready — logged in as %s (id=%s)", self.user, self.user.id)

    async def on_message(self, message: discord.Message) -> None:
        """Called for every message the bot can see."""
        # Ignore all bot messages (prevents feedback loops)
        if message.author.bot:
            return

        if not contains_trigger(message.content):
            return

        _log_trigger(message)

        gif_url = pick_gif()
        try:
            await message.reply(gif_url, mention_author=False)
        except discord.Forbidden:
            log.warning(
                "Missing permission to send messages in channel %s", message.channel.id
            )
        except discord.HTTPException as exc:
            log.error("Discord API error when replying: %s", exc)


def main() -> None:
    """Entry point: validate config, build intents, and run the bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        log.critical(
            "DISCORD_TOKEN not set. Create a .env file with DISCORD_TOKEN=<your token>."
        )
        sys.exit(1)

    if not GIFS:
        log.critical("GIFS list in config.py is empty. Add at least one GIF URL.")
        sys.exit(1)

    intents = discord.Intents.default()
    intents.message_content = True  # Required to read message text

    client = IdyBot(intents=intents)

    try:
        client.run(token, log_handler=None)  # We manage our own logging
    except discord.LoginFailure:
        log.critical("Invalid Discord token. Double-check your DISCORD_TOKEN in .env.")
        sys.exit(1)


if __name__ == "__main__":
    main()
