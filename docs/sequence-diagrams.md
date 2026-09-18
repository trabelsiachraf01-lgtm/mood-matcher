# Sequence diagrams

Two request flows, chosen by the `songSource` toggle in step 1. Both always fetch a matched
photo; only the song differs.

## 1. Catalog match (`songSource=catalog`, the default)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as /suggestions
    participant SS as SuggestionService
    participant MA as MoodAnalyzer
    participant Repo as CatalogRepository

    U->>FE: submit (image / audio / text)
    FE->>API: POST /suggestions (songSource=catalog)
    API->>SS: suggest()
    SS->>MA: analyze(input)
    par caption (OpenRouter)
        MA->>MA: caption_image/audio/text
    and embed (EBind, local)
        MA->>MA: embed_image/audio/text
    end
    MA-->>SS: caption + embedding
    SS->>Repo: nearest_images(embedding)
    SS->>Repo: nearest_songs(embedding)
    Repo-->>SS: image match, song match
    SS-->>API: caption, matchedMedia, nowPlaying
    API-->>FE: 200 SuggestionResponse
    FE->>U: step 2 — hero image + song autoplaying
```

## 2. Generate with ElevenLabs (`songSource=generate`)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as /suggestions
    participant SS as SuggestionService
    participant Gen as /generate-music
    participant MG as MusicGenerator
    participant EL as ElevenLabs Music API

    U->>FE: submit + "Generate with ElevenLabs"
    FE->>API: POST /suggestions (songSource=generate)
    API->>SS: suggest()
    Note over SS: song lookup skipped entirely —<br/>nearest_songs() never runs
    SS-->>API: caption, matchedMedia, nowPlaying=empty
    API-->>FE: 200 SuggestionResponse
    Note over FE: step 1 stays put, showing a<br/>progress bar — step 2 hasn't rendered yet
    FE->>Gen: POST /generate-music (prompt=caption)
    Gen->>MG: generate(prompt)
    MG->>EL: POST /v1/music/compose
    EL-->>MG: audio/mpeg bytes
    MG-->>Gen: audio bytes
    Gen-->>FE: 200 audio/mpeg
    FE->>FE: blob → object URL → swap into nowPlaying
    FE->>U: step 2 — hero image + generated track already playing
```
