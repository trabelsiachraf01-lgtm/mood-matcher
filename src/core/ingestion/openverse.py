"""Real ingestion: pulls CC-licensed/public-domain images from Openverse by mood keyword,
embeds each with EBind, and stores them in the `images` table (schema.sql). No API key
needed — Openverse's search endpoint is open.

Run: python -m src.core.ingestion.openverse
"""

from __future__ import annotations

import httpx

from src.core.embedding.embedder import embed_image
from src.core.indexing.store import CatalogRepository, get_connection
from src.core.media import download

BASE_URL = "https://api.openverse.org/v1/images/"

# 10 queries x 10 images = 100 — broad enough mood coverage that matches don't just cluster
# around a handful of queries.
MOOD_QUERIES = [
    "golden hour", "melancholy", "cozy night", "quiet morning", "urban energy",
    "rainy day", "autumn leaves", "ocean waves", "city lights", "peaceful forest",
]
PAGE_SIZE = 10


def fetch_images(client: httpx.Client, query: str, page_size: int) -> list[dict]:
    response = client.get(
        BASE_URL,
        params={"q": query, "page_size": page_size, "license_type": "commercial,modification"},
    )
    response.raise_for_status()
    return response.json()["results"]


def main() -> None:
    repo = CatalogRepository(get_connection())

    with httpx.Client(timeout=30.0) as client:
        for query in MOOD_QUERIES:
            results = fetch_images(client, query, PAGE_SIZE)
            count = 0
            for item in results:
                try:
                    image_path = download(item["url"], ".jpg")
                    embedding = embed_image(str(image_path))
                except Exception as exc:  # noqa: BLE001 — one bad image shouldn't stop the run
                    print(f"  skip {item['id']}: {exc}")
                    continue

                repo.upsert_image(
                    source="openverse",
                    source_id=item["id"],
                    title=item["title"] or query,
                    url=item["foreign_landing_url"],
                    asset_url=item["url"],
                    license=f"{item['license'].upper()} {item.get('license_version', '')}".strip(),
                    attribution=item.get("creator") or "Unknown",
                    embedding=embedding,
                )
                count += 1

            print(f"{query}: ingested {count}/{len(results)}")


if __name__ == "__main__":
    main()
