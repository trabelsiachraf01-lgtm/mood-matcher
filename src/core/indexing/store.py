"""Data-access layer over the songs/images tables (schema.sql). Plain psycopg, no ORM,
since two tables and a handful of queries don't need one.
"""

from __future__ import annotations

from dataclasses import dataclass

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from src.core.config import DATABASE_URL


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    register_vector(conn)
    return conn


@dataclass(frozen=True)
class Song:
    id: str
    title: str
    artist: str
    url: str
    asset_url: str | None
    license: str
    distance: float = 0.0


@dataclass(frozen=True)
class Image:
    id: str
    title: str
    url: str
    asset_url: str | None
    license: str
    attribution: str
    distance: float = 0.0


class CatalogRepository:
    """Owns all reads/writes against the songs and images tables for one connection."""

    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def upsert_song(
        self,
        *,
        source: str,
        source_id: str,
        title: str,
        artist: str,
        url: str,
        asset_url: str,
        license: str,
        embedding: list[float],
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO songs (source, source_id, title, artist, url, asset_url, license, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_id) DO UPDATE SET
                title = EXCLUDED.title, artist = EXCLUDED.artist, url = EXCLUDED.url,
                asset_url = EXCLUDED.asset_url, license = EXCLUDED.license,
                embedding = EXCLUDED.embedding
            """,
            (source, source_id, title, artist, url, asset_url, license, embedding),
        )

    def upsert_image(
        self,
        *,
        source: str,
        source_id: str,
        title: str,
        url: str,
        asset_url: str,
        license: str,
        attribution: str,
        embedding: list[float],
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO images (source, source_id, title, url, asset_url, license, attribution, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_id) DO UPDATE SET
                title = EXCLUDED.title, url = EXCLUDED.url, asset_url = EXCLUDED.asset_url,
                license = EXCLUDED.license, attribution = EXCLUDED.attribution,
                embedding = EXCLUDED.embedding
            """,
            (source, source_id, title, url, asset_url, license, attribution, embedding),
        )

    def nearest_songs(self, embedding: list[float], limit: int = 5) -> list[Song]:
        rows = self._conn.execute(
            """
            SELECT id, title, artist, url, asset_url, license, embedding <=> %s AS distance
            FROM songs ORDER BY distance LIMIT %s
            """,
            (Vector(embedding), limit),
        ).fetchall()
        return [Song(str(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]

    def nearest_images(self, embedding: list[float], limit: int = 5) -> list[Image]:
        rows = self._conn.execute(
            """
            SELECT id, title, url, asset_url, license, attribution, embedding <=> %s AS distance
            FROM images ORDER BY distance LIMIT %s
            """,
            (Vector(embedding), limit),
        ).fetchall()
        return [Image(str(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]

    def all_songs(self) -> list[Song]:
        rows = self._conn.execute(
            "SELECT id, title, artist, url, asset_url, license FROM songs ORDER BY created_at"
        ).fetchall()
        return [Song(str(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]

    def all_images(self) -> list[Image]:
        rows = self._conn.execute(
            "SELECT id, title, url, asset_url, license, attribution FROM images ORDER BY created_at"
        ).fetchall()
        return [Image(str(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]

    def counts(self) -> tuple[int, int]:
        songs = self._conn.execute("SELECT count(*) FROM songs").fetchone()[0]
        images = self._conn.execute("SELECT count(*) FROM images").fetchone()[0]
        return songs, images
