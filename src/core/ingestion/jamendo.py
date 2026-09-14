"""Real ingestion: pulls Creative-Commons-licensed tracks from Jamendo by mood tag, embeds
each with EBind, and stores them in the `songs` table (schema.sql). Requires
JAMENDO_CLIENT_ID (free, https://devportal.jamendo.com) in .env.

Run: python -m src.core.ingestion.jamendo
"""

from __future__ import annotations

import httpx

from src.core.config import JAMENDO_CLIENT_ID
from src.core.embedding.embedder import embed_audio
from src.core.indexing.store import get_connection, upsert_song
from src.core.media import download, transcode_to_wav

BASE_URL = "https://api.jamendo.com/v3.0/tracks"

# Small on purpose — enough to prove the pipeline works, not a real catalog size.
MOOD_TAGS = ["melancholy", "upbeat", "chill", "energetic", "cozy"]
LIMIT = 5


def fetch_tracks(client: httpx.Client, tag: str, limit: int) -> list[dict]:
    response = client.get(
        BASE_URL,
        params={
            "client_id": JAMENDO_CLIENT_ID,
            "format": "json",
            "limit": limit,
            "tags": tag,
            "include": "licenses",
            "audioformat": "mp32",
        },
    )
    response.raise_for_status()
    return response.json()["results"]


def main() -> None:
    if not JAMENDO_CLIENT_ID:
        raise RuntimeError("JAMENDO_CLIENT_ID is not set — get a free one at devportal.jamendo.com")

    conn = get_connection()

    with httpx.Client(timeout=30.0) as client:
        for tag in MOOD_TAGS:
            results = fetch_tracks(client, tag, LIMIT)
            count = 0
            for item in results:
                try:
                    audio_path = download(item["audio"], ".mp3")
                    wav_path = transcode_to_wav(audio_path)
                    embedding = embed_audio(str(wav_path))
                except Exception as exc:  # noqa: BLE001 — one bad track shouldn't stop the run
                    print(f"  skip {item['id']}: {exc}")
                    continue

                upsert_song(
                    conn,
                    source="jamendo",
                    source_id=str(item["id"]),
                    title=item["name"],
                    artist=item["artist_name"],
                    url=item["shareurl"],
                    license=item.get("license_ccurl", "CC"),
                    embedding=embedding,
                )
                count += 1

            print(f"{tag}: ingested {count}/{len(results)}")


if __name__ == "__main__":
    main()
