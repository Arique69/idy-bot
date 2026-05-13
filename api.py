"""FastAPI server for Discord Activity frontend.

Run alongside the bot:
  uvicorn api:app --host 0.0.0.0 --port 8000 --ssl-keyfile /etc/letsencrypt/live/idy-api.duckdns.org/privkey.pem --ssl-certfile /etc/letsencrypt/live/idy-api.duckdns.org/fullchain.pem
"""

from __future__ import annotations

import json
import os
import asyncio
import random
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import CARDS, RARITY_CONFIG
from data import load_data, get_user

app = FastAPI(title="idy-bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

CARD_LOOKUP: dict[str, dict] = {c["name"]: c for c in CARDS}

RARITY_ORDER = ["special", "mythic", "legendary", "epic", "rare", "common"]


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/user/{discord_id}/collection")
def get_collection(discord_id: str):
    data = load_data()
    user = get_user(data, discord_id)
    collection = user.get("collection", {})

    result = {}
    for name, count in collection.items():
        card = CARD_LOOKUP.get(name)
        if card is None:
            continue
        if card["rarity"] == "special":
            continue
        result[name] = {
            "rarity": card["rarity"],
            "url": card["url"],
            "power": card["power"],
            "count": count,
        }
    return result


@app.get("/user/{discord_id}/stats")
def get_stats(discord_id: str):
    data = load_data()
    user = get_user(data, discord_id)
    collection = user.get("collection", {})

    total_unique = sum(
        1 for name, cnt in collection.items()
        if cnt > 0 and CARD_LOOKUP.get(name, {}).get("rarity") != "special"
    )
    total_cards = sum(
        cnt for name, cnt in collection.items()
        if CARD_LOOKUP.get(name, {}).get("rarity") != "special"
    )

    return {
        "totalUnique": total_unique,
        "totalCards": total_cards,
        "duelWins": user.get("duel_wins", 0),
        "duelLosses": user.get("duel_losses", 0),
        "duelDraws": user.get("duel_draws", 0),
        "coins": user.get("coins", 0),
    }


DUEL_WIN_REWARD = 10
REROLL_COST = 5

@app.post("/user/{discord_id}/duel/win")
def duel_win(discord_id: str):
    data = load_data()
    user = get_user(data, discord_id)
    user["duel_wins"] = user.get("duel_wins", 0) + 1
    user["coins"] = user.get("coins", 0) + DUEL_WIN_REWARD
    from data import save_data
    save_data(data)
    return {"coins": user["coins"]}

@app.post("/user/{discord_id}/duel/loss")
def duel_loss(discord_id: str):
    data = load_data()
    user = get_user(data, discord_id)
    user["duel_losses"] = user.get("duel_losses", 0) + 1
    from data import save_data
    save_data(data)
    return {"ok": True}

@app.post("/user/{discord_id}/reroll")
def reroll_hand(discord_id: str):
    data = load_data()
    user = get_user(data, discord_id)

    if user.get("coins", 0) < REROLL_COST:
        raise HTTPException(status_code=400, detail="Not enough coins")

    user["coins"] -= REROLL_COST
    from data import save_data
    save_data(data)

    # draw new hand from user's collection
    collection = user.get("collection", {})
    available = [
        {**CARD_LOOKUP[name], "count": cnt}
        for name, cnt in collection.items()
        if name in CARD_LOOKUP and CARD_LOOKUP[name]["rarity"] != "special"
    ]

    if len(available) < 5:
        pool = [c for c in CARDS if c["rarity"] != "special"]
        random.shuffle(pool)
        available = pool[:5]

    hand = random.sample(available, min(5, len(available)))
    return {"coins": user["coins"], "hand": hand}


# ---------------------------------------------------------------------------
# WebSocket duel matchmaking
# ---------------------------------------------------------------------------

class DuelManager:
    def __init__(self):
        self.queue: list[tuple[str, WebSocket]] = []
        self.rooms: dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def join_queue(self, user_id: str, ws: WebSocket):
        async with self._lock:
            # check if someone is already waiting
            if self.queue:
                opponent_id, opponent_ws = self.queue.pop(0)
                room_id = f"{opponent_id}-{user_id}"

                hand_a = self._draw_hand(opponent_id)
                hand_b = self._draw_hand(user_id)

                self.rooms[room_id] = {
                    "players": {
                        opponent_id: {"ws": opponent_ws, "hand": hand_a, "pick": None},
                        user_id:     {"ws": ws,          "hand": hand_b, "pick": None},
                    },
                    "scores": {opponent_id: 0, user_id: 0},
                    "round": 1,
                }

                await opponent_ws.send_json({
                    "type": "match_found",
                    "room_id": room_id,
                    "hand": hand_a,
                })
                await ws.send_json({
                    "type": "match_found",
                    "room_id": room_id,
                    "hand": hand_b,
                })
            else:
                self.queue.append((user_id, ws))
                await ws.send_json({"type": "waiting"})

    def _draw_hand(self, user_id: str, count: int = 5) -> list[dict]:
        data = load_data()
        user = get_user(data, user_id)
        collection = user.get("collection", {})

        available = [
            {**CARD_LOOKUP[name], "count": cnt}
            for name, cnt in collection.items()
            if name in CARD_LOOKUP and CARD_LOOKUP[name]["rarity"] != "special"
        ]

        if len(available) < count:
            # pad with random cards from global pool if collection too small
            pool = [c for c in CARDS if c["rarity"] != "special"]
            random.shuffle(pool)
            available = pool[:count]

        return random.sample(available, min(count, len(available)))

    async def pick_card(self, room_id: str, user_id: str, card_name: str):
        if room_id not in self.rooms:
            return
        room = self.rooms[room_id]
        if user_id not in room["players"]:
            return

        room["players"][user_id]["pick"] = card_name

        picks = {uid: p["pick"] for uid, p in room["players"].items()}
        if all(p is not None for p in picks.values()):
            await self._resolve_round(room_id)

    async def _resolve_round(self, room_id: str):
        room = self.rooms[room_id]
        players = list(room["players"].keys())
        a_id, b_id = players[0], players[1]
        pick_a = room["players"][a_id]["pick"]
        pick_b = room["players"][b_id]["pick"]

        card_a = CARD_LOOKUP.get(pick_a)
        card_b = CARD_LOOKUP.get(pick_b)

        rank_a = RARITY_ORDER.index(card_a["rarity"]) if card_a else 999
        rank_b = RARITY_ORDER.index(card_b["rarity"]) if card_b else 999

        if rank_a < rank_b:
            winner = a_id
        elif rank_b < rank_a:
            winner = b_id
        else:
            winner = None  # draw

        if winner:
            room["scores"][winner] += 1

        result_payload = {
            "type": "round_result",
            "round": room["round"],
            "picks": {a_id: pick_a, b_id: pick_b},
            "winner": winner,
            "scores": room["scores"],
        }

        for uid, p in room["players"].items():
            try:
                await p["ws"].send_json(result_payload)
            except Exception:
                pass

        # check if game over (BO3 → first to 2)
        max_score = max(room["scores"].values())
        if max_score >= 2:
            await self._end_game(room_id)
        else:
            # next round
            room["round"] += 1
            for uid in players:
                room["players"][uid]["pick"] = None
                new_hand = self._draw_hand(uid)
                room["players"][uid]["hand"] = new_hand
                try:
                    await room["players"][uid]["ws"].send_json({
                        "type": "next_round",
                        "round": room["round"],
                        "hand": new_hand,
                    })
                except Exception:
                    pass

    async def _end_game(self, room_id: str):
        room = self.rooms[room_id]
        players = list(room["players"].keys())
        scores = room["scores"]
        winner = max(scores, key=lambda u: scores[u])

        # save results to data.json
        data = load_data()
        for uid in players:
            user = get_user(data, uid)
            if uid == winner:
                user["duel_wins"] = user.get("duel_wins", 0) + 1
                user["coins"] = user.get("coins", 0) + 10
            else:
                user["duel_losses"] = user.get("duel_losses", 0) + 1
        from data import save_data
        save_data(data)

        for uid, p in room["players"].items():
            try:
                await p["ws"].send_json({
                    "type": "game_over",
                    "scores": scores,
                    "winner": winner,
                })
            except Exception:
                pass

        del self.rooms[room_id]

    def remove_from_queue(self, user_id: str):
        self.queue = [(uid, ws) for uid, ws in self.queue if uid != user_id]


duel_manager = DuelManager()


@app.websocket("/ws/{user_id}")
async def duel_ws(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        await duel_manager.join_queue(user_id, websocket)

        async for message in websocket.iter_json():
            msg_type = message.get("type")
            if msg_type == "pick":
                await duel_manager.pick_card(
                    message["room_id"],
                    user_id,
                    message["card_name"],
                )
            elif msg_type == "cancel":
                duel_manager.remove_from_queue(user_id)
                await websocket.send_json({"type": "cancelled"})

    except WebSocketDisconnect:
        duel_manager.remove_from_queue(user_id)
