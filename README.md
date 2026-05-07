# idy-bot

A Discord bot that replies with a random GIF whenever someone says "idy" (whole word, case-insensitive).

---

## 1 — Create a Discord Application & Bot

1. Go to <https://discord.com/developers/applications> and click **New Application**.
2. Give it a name, then open the **Bot** tab on the left sidebar.
3. Click **Add Bot** → **Yes, do it!**
4. Under the bot's username, click **Reset Token**, copy it, and keep it secret — this goes in your `.env`.

---

## 2 — Enable the Message Content Intent

Still on the **Bot** tab, scroll down to **Privileged Gateway Intents** and toggle **Message Content Intent** ON. Save changes.

> Without this, the bot cannot read message text and will never trigger.

---

## 3 — Invite the Bot to Your Server

1. Go to the **OAuth2 → URL Generator** tab.
2. Under **Scopes**, check `bot`.
3. Under **Bot Permissions**, check:
   - `Send Messages`
   - `Read Message History`
4. Copy the generated URL, open it in a browser, and select the server you want to add the bot to.

---

## 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

Python 3.10+ is required.

---

## 5 — Set Up `.env`

Copy the example file and fill in your token:

```bash
cp .env.example .env
```

Edit `.env`:

```
DISCORD_TOKEN=your_actual_bot_token_here
```

**Never commit `.env` — it is already in `.gitignore`.**

---

## 6 — Run the Bot

```bash
python bot.py
```

You should see:

```
2026-05-07 12:00:00 [INFO] Bot ready — logged in as idy-bot#1234 (id=123456789)
```

The bot will now respond in any channel it can read and write in.

---

## 7 — Customize GIFs and the Trigger Word

Open `config.py`:

```python
TRIGGER_WORD: str = "idy"   # Change to any word

GIFS: list[str] = [
    "https://media.tenor.com/your-gif-1.gif",
    "https://media.tenor.com/your-gif-2.gif",
    # Add as many as you like
]
```

- Replace the placeholder URLs with real Tenor or Giphy URLs — Discord will auto-embed them.
- To add support for more trigger words later, add entries to a `TRIGGERS` list and iterate over them in `bot.py`'s `contains_trigger`.

---

## Console Log Format

Each trigger event is logged like:

```
2026-05-07 12:01:23 [INFO] Trigger | 2026-05-07 12:01:23 UTC | guild=My Server channel=#general user=someone#0001
```

Message content is intentionally **not** logged for privacy.
