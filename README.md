# Anidle (Wordle v2 – Animal Guessing)

**Tech stack:** FastAPI (Python) backend, HTML/CSS + Brython (Python-in-browser) frontend.  
**Goal:** Guess the hidden animal by its traits. Default mode: **Free Play**, **6 attempts**.  
Keep project **standalone** — do not modify the old Wordle repo.

## Requirements

- Python **3.11+**
- pip ≥ 23
- Git (optional)

## Run (dev)

```bash
py -3.12 -m venv .venv
.venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn api:app --reload
```

Then open: http://localhost:8000/

## Project Tree

```
anidle/
  api.py                 # FastAPI app (endpoints + static/template serving)
  game/
    animals.py           # Dataset loader + search
    utils.py             # Feedback scoring for traits & optional letter feedback
    schemas.py           # Pydantic models
    data/
      animals.json       # Seed dataset (expandable)
      animals.schema.json# JSON Schema for validation
  templates/
    index.html           # App shell
  static/
    style.css            # Minimal styles + animations
    app.py               # Brython frontend logic
  requirements.txt
  README.md
```

## API (contract)

- `POST /api/new` → `{game_id, max_attempts, settings}`
- `POST /api/guess` `{game_id, guess}` → feedback object (trait + optional letter feedback)
- `GET /api/animals?q=...` → autocomplete list
- `GET /api/daily` → deterministic daily seed (no spoilers)

## Notes

- **English names**, **spaces/hyphens allowed**, case-insensitive.
- Default **Free Play** (Daily available).
- **Attempts = 5**.
- **Traits:** class, diet, habitat[], continents[], size_kg (↑/↓/≈), lifespan_years (↑/↓/≈).
- Difficulty tiers (easy/normal/hard) toggle hints in the UI; server always returns full trait feedback (client can hide by mode).
