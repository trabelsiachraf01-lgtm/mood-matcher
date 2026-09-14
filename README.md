# Mood Matcher

Give it an image, a song, or a line of text describing a mood, and get back a generated
caption plus a real matched song/image — with attribution and a link to the real source,
never AI-generated media.

Cross-modal matching runs on [EBind](https://github.com/encord-team/ebind); captioning runs
on Qwen3-VL and Gemini Flash via OpenRouter. There's no real catalog yet — the backend
currently matches against a 2-item in-memory fixture (one image, one placeholder tone) just
to prove the loop works end-to-end. See **Coming next** below.

## Run it locally

Two terminals.

**Backend** (from the repo root):

```bash
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt                      # first time only
brew install ffmpeg                                   # first time only, macOS
cp .env.example .env                                  # first time only — fill in OPENROUTER_API_KEY

DYLD_LIBRARY_PATH="/opt/homebrew/lib" uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

The `DYLD_LIBRARY_PATH` is a macOS-only quirk — without it, `torchcodec` can't find
Homebrew's `ffmpeg` libs and audio embedding fails silently. First request after startup
takes a few seconds (loading EBind, building the fixture catalog).

**Frontend** (from `frontend/`):

```bash
npm install   # first time only
npm run dev
```

Open **http://localhost:5173**. The backend must already be running — the frontend calls
`http://localhost:8000/suggestions` directly, no mock fallback.

### Tests

```bash
pytest tests/integration -v
```

Real model weights, real API calls — not free, not instant. `test_embedding.py` needs no
API key; `test_captioning.py` needs `OPENROUTER_API_KEY` set.

## Coming next: the ingestion pipeline

The in-memory fixture proves captioning + embedding + matching all work — what it can't
prove is real recommendation quality, since it only ever has one image and one (synthetic,
non-musical) tone to match against. Next step replaces that with a real catalog:

- Pull Creative-Commons-licensed tracks from the **Jamendo API** and CC-licensed/public-domain
  images from **Openverse**, by mood/theme keyword.
- Embed each with EBind and store in **pgvector on Postgres** — chosen over a dedicated
  vector DB so relational data (profile, preferences) can live in the same instance later.
- Swap the `/suggestions` endpoint's matching step from the 2-item fixture to a real
  cosine-similarity query against that store.

No migrations, no ORM layer, no ingestion abstractions until this is actually being built —
build one slice at a time, prove it works, then move on.
