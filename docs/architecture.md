# Architecture

Three layers: a thin HTTP boundary, the services that hold all real logic, and the
clients/storage each service calls through. Nothing outside `src/api` knows about FastAPI,
and nothing outside `src/core/clients`/`src/core/indexing` knows how a given external system
is actually called — that's what lets `MoodAnalyzer` or `SuggestionService` be tested without
a server or a database.

```mermaid
flowchart TD
    subgraph Frontend["frontend/ (React wizard)"]
        UI["StepInput / StepResults"]
    end

    subgraph API["src/api/app.py"]
        Suggest["POST /suggestions"]
        Generate["POST /generate-music"]
    end

    subgraph Services["src/core/services"]
        SS["SuggestionService"]
        MA["MoodAnalyzer"]
        MG["MusicGenerator"]
    end

    subgraph Clients["src/core/clients + embedding"]
        OR["openrouter.chat\n(VISION_MODEL / AUDIO_MODEL / TEXT_MODEL)"]
        EB["embedder.embed_*\n(EBind, local)"]
        EL["elevenlabs.compose\n(Music API)"]
    end

    subgraph Storage["src/core/indexing/store.py"]
        Repo["CatalogRepository"]
        PG[("Postgres + pgvector")]
    end

    subgraph Ingestion["src/core/ingestion (offline, run manually)"]
        Jam["jamendo.py"]
        Open["openverse.py"]
    end

    UI -->|"multipart form\n(image, song, or text)"| Suggest
    Suggest -.->|"caption"| UI
    UI -->|"caption as prompt\n(any input mode)"| Generate

    Suggest --> SS
    Generate --> MG

    SS --> MA
    MA --> OR
    MA --> EB
    SS -->|"nearest_images / nearest_songs\n(skipped when songSource=generate)"| Repo

    MG --> EL

    Repo <--> PG
    Jam --> EB
    Open --> EB
    Jam --> Repo
    Open --> Repo
```

## Why it's split this way

- **`SuggestionService` never calls an external generation API.** It only ever reads from
  the catalog (`CatalogRepository`). Generation lives entirely in `MusicGenerator`, called
  from its own endpoint (`/generate-music`), so a slow or misconfigured ElevenLabs key can
  never block the normal match path.
- **`MoodAnalyzer` dispatches on input mode but produces the same shape** (`caption` +
  `embedding`) regardless of whether the input was an image, an audio file, or text — so
  `SuggestionService` doesn't need to know which mode ran.
- **`songSource` is independent of input mode.** Every input — image, song, or text — comes
  back from `/suggestions` with a caption, and that caption is what `/generate-music` takes
  as its prompt. Uploading an image and picking "Generate with ElevenLabs" works exactly the
  same way text input does; nothing about generation is text-only.
- **Captioning (network) and embedding (local EBind inference) run concurrently**
  (`ThreadPoolExecutor`, one future each) since neither depends on the other's result —
  see `_analyze_image`/`_analyze_audio`/`_analyze_text` in `mood_analyzer.py`.
- **Ingestion is offline and one-directional.** `jamendo.py`/`openverse.py` populate the
  catalog ahead of time; nothing in the request path ever calls them.
