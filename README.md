# Hushtone

Give it an image, a song, or a line of text describing a mood, and get back a generated
caption plus a real matched song/image — with attribution and a link to the real source,
never AI-generated media by default.

Cross-modal matching runs on [EBind](https://github.com/encord-team/ebind); captioning runs
on Gemini Flash-Lite via OpenRouter for every input mode (picked by benchmarking against a
few alternatives — see `VISION_MODEL`/`AUDIO_MODEL`/`TEXT_MODEL` in `src/core/config.py`);
the catalog is real Creative-Commons tracks from **Jamendo** and CC-licensed/public-domain
images from **Openverse**, embedded and stored in **Postgres + pgvector**. Every match
always comes back with both a real image and a real song, regardless of what you searched
with.

Instead of a catalog match, you can also have the song **generated on the spot** by
[ElevenLabs Music](https://elevenlabs.io/music) — pick "Generate with ElevenLabs" in step 1.

Every request logs how long captioning, embedding, and (for audio) transcoding each took, plus
the winning match's distance score — check the backend's stdout.

## Demo 



[Video](https://github.com/user-attachments/assets/7619314b-46a2-4ebc-882b-a111e9760114) 



## Architecture

- [`docs/architecture.md`](docs/architecture.md) — component diagram and why the layers are
  split the way they are.
- [`docs/sequence-diagrams.md`](docs/sequence-diagrams.md) — request flow for a catalog match
  vs. an ElevenLabs-generated song.

## Run it locally

One command:

```bash
cp .env.example .env   # first time only — fill in OPENROUTER_API_KEY, JAMENDO_CLIENT_ID
                        # ELEVENLABS_API_KEY is optional — only needed for the
                        # "Generate with ElevenLabs" button, and requires a paid
                        # ElevenLabs plan (the Music API isn't on the free tier)

docker compose up --build
```

Requires Docker. This project uses [Colima](https://github.com/abiosoft/colima) as a free,
headless Docker runtime on macOS (`brew install colima docker docker-compose && colima start`)
— Docker Desktop works the same if you already have it.

That builds and starts the database (with `schema.sql` applied automatically on first boot),
the backend on **http://localhost:8000**, and the frontend on **http://localhost:5173**. Both
backend and frontend bind-mount the source tree and run in reload/dev mode, so local edits pick
up live, same as running them directly. First request after startup takes a few seconds
(loading EBind).

### Run without Docker

Three terminals — useful for debugging with a local Python/Node toolchain directly.

**Database**:

```bash
docker compose up -d db
```

**Backend** (from the repo root):

```bash
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r requirements.txt                      # first time only
brew install ffmpeg                                   # first time only, macOS
cp .env.example .env                                  # first time only, see above

DYLD_LIBRARY_PATH="/opt/homebrew/lib" uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

The `DYLD_LIBRARY_PATH` is a macOS-only quirk — without it, `torchcodec` can't find
Homebrew's `ffmpeg` libs and audio embedding fails silently. Not needed in the Docker path,
which runs on Linux.

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
docker compose run --rm backend python -m src.core.ingestion.openverse   # no API key needed
docker compose run --rm backend python -m src.core.ingestion.jamendo     # needs JAMENDO_CLIENT_ID

# without Docker: drop the `docker compose run --rm backend` prefix
```

Each pulls tracks/images across 10 mood keywords (~10 items per keyword, ~100 rows total),
embeds them with EBind, and upserts into Postgres — re-running is safe, it updates existing
rows by source id rather than duplicating them.

### Tests

```bash
pytest tests/integration -v
```

Real model weights, real API calls — not free, not instant. `test_embedding.py` needs no
API key; `test_captioning.py` needs `OPENROUTER_API_KEY` set.

## Coming next

The catalog (~100 songs, ~100 images) is still intentionally small next to a real product
catalog, but big enough that matches don't just cluster around a handful of search terms.
Growing it further is just running ingestion with a longer keyword list. Beyond that: no
migrations, no ORM layer, no ingestion
abstractions until something concrete actually needs them — build one slice at a time, prove
it works, then move on.
