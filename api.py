from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import uuid, time, datetime
import random

from game.animals import AnimalDB, normalize
from game.utils import trait_feedback, letter_feedback, sanitize_name
from game.schemas import NewGameRequest, NewGameResponse, GuessRequest, GuessResponse, AnimalsResponse

app = FastAPI(title="Anidle")
import os
ANIDLE_DEBUG = os.getenv("ANIDLE_DEBUG", "1") == "1"

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DB = AnimalDB()
DB.load()

TTL_SECONDS = 60 * 60 * 12
GAMES: Dict[str, Dict[str, Any]] = {}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/new", response_model=NewGameResponse)
def api_new(req: NewGameRequest):
    now = time.time()
    for gid in list(GAMES):
        if now - GAMES[gid]["ts"] > TTL_SECONDS:
            GAMES.pop(gid, None)

    gid = uuid.uuid4().hex
    idx = random.randrange(len(DB.items))

    target = DB.items[idx]
    GAMES[gid] = {
        "target": target,
        "attempts": [],
        "max_attempts": 6,
        "letter_feedback": bool(req.letter_feedback),
        "ts": now,
    }

    if ANIDLE_DEBUG:
        print(f"[ANIDLE DEBUG] new game {gid} -> answer={target['name_en']} {target.get('emoji','')}")

    return NewGameResponse(game_id=gid, max_attempts=6, settings={"mode": req.mode})

@app.post("/api/guess", response_model=GuessResponse)
def api_guess(req: GuessRequest):
    game = GAMES.get(req.game_id)
    if not game:
        return JSONResponse({"error":"invalid-game"}, status_code=400)
    if len(game["attempts"]) >= game["max_attempts"]:
        return JSONResponse({"error":"game-finished","answer":game['target']['name_en']}, status_code=400)

    guess_name = normalize(req.guess)
    guess_obj = DB.get(guess_name)
    if not guess_obj:
        return JSONResponse({"error":"not-in-dictionary"}, status_code=400)

    tf = trait_feedback(game["target"], guess_obj)

    lf = None
    if game.get("letter_feedback"):
        ans = sanitize_name(game["target"]["name_en"])
        gsn = sanitize_name(guess_obj["name_en"])
        lf = letter_feedback(ans, gsn)

    state = "in_progress"
    if guess_obj["name_en"].lower() == game["target"]["name_en"].lower():
        state = "won"
    elif len(game["attempts"]) + 1 >= game["max_attempts"]:
        state = "lost"

    game["attempts"].append({"guess": guess_obj["name_en"], "tf": tf, "won": state=="won"})

    out = {
        "status": state,
        "attempt": len(game["attempts"]),
        "trait_feedback": tf,
        "letter_feedback": lf,
    }
    if state in ("won","lost"):
        out["answer"] = game["target"]["name_en"]
    return out

@app.get("/api/animals") 
def api_animals(q: str = "", details: bool = False):
    if not details:
        names = DB.search(q, 30)                 
        return {"items": names}

    qn = normalize(q)
    items = []
    for a in DB.items:
        if qn in normalize(a.get("name_en", "")):
            items.append({
                "name_en": a.get("name_en"),
                "emoji": a.get("emoji"),
                "class": a.get("class"),
                "diet": a.get("diet"),
                "habitat": (a.get("habitat") or [])[:2],
            })
            if len(items) >= 30:
                break
    return {"items": items}
