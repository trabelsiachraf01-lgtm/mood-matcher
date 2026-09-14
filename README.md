# Hushtone

Give it an image, a song, or a line of text describing a mood, and get back a generated
caption plus a real matched song/image — with attribution and a link to the real source,
never AI-generated media.

Cross-modal matching runs on [EBind](https://github.com/encord-team/ebind); captioning runs
on Qwen3-VL and Gemini Flash via OpenRouter; the catalog is real Creative-Commons tracks from
**Jamendo** and CC-licensed/public-domain images from **Openverse**, embedded and stored in
**Postgres + pgvector**.

## Run it locally

Three terminals.

**Database** (from the repo root):

```bash
docker compose up -d               # first time only pulls the pgvector/pgvector:pg16 image
docker exec -i mood-matcher-db-1 psql -U mood_matcher -d mood_matcher < schema.sql   # first time only
```

Requires Docker. This project uses [Colima](https://github.com/abiosoft/colima) as a free,
headless Docker runtime on macOS (`brew install colima docker docker-compose && colima start`)
— Docker Desktop works the same if you already have it.

**Backend** (from the repo root):

```bash
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt                      # first time only
brew install ffmpeg                                   # first time only, macOS
cp .env.example .env                                  # first time only — fill in OPENROUTER_API_KEY, JAMENDO_CLIENT_ID

DYLD_LIBRARY_PATH="/opt/homebrew/lib" uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

The `DYLD_LIBRARY_PATH` is a macOS-only quirk — without it, `torchcodec` can't find
Homebrew's `ffmpeg` libs and audio embedding fails silently. First request after startup
takes a few seconds (loading EBind).

**Frontend** (from `frontend/`):

```bash
npm install   # first time only
npm run dev
```

Open **http://localhost:5173**. The backend must already be running — the frontend calls
`http://localhost:8000/suggestions` directly, no mock fallback.

### Populate the catalog

The database starts empty — nothing to match against until you run ingestion at least once:

```bash
python -m src.core.ingestion.openverse   # no API key needed
python -m src.core.ingestion.jamendo     # needs JAMENDO_CLIENT_ID (free, devportal.jamendo.com)
```

Each pulls a small set of tracks/images across a handful of mood keywords, embeds them with
EBind, and upserts into Postgres — re-running is safe, it updates existing rows by source id
rather than duplicating them.

### Tests

```bash
pytest tests/integration -v
```

Real model weights, real API calls — not free, not instant. `test_embedding.py` needs no
API key; `test_captioning.py` needs `OPENROUTER_API_KEY` set.

## Coming next

The catalog is intentionally small (a few dozen rows per mood keyword) — enough to prove
matching quality is real, not enough to be a real product catalog. Growing it is just running
ingestion with a longer keyword list. Beyond that: no migrations, no ORM layer, no ingestion
abstractions until something concrete actually needs them — build one slice at a time, prove
it works, then move on.
