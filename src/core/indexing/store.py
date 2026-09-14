"""Thin data-access layer over the songs/images tables (schema.sql). Replaces
src/core/embedding/fixtures.py's in-memory catalog now that real ingestion exists — plain
psycopg, no ORM, since two tables and four queries don't need one.
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
    license: str
    distance: float


@dataclass(frozen=True)
class Image:
    id: str
    title: str
    url: str
    license: str
    attribution: str
    distance: float


def upsert_song(
    conn: psycopg.Connection,
    *,
    source: str,
    source_id: str,
    title: str,
    artist: str,
    url: str,
    license: str,
    embedding: list[float],
) -> None:
    conn.execute(
        """
        INSERT INTO songs (source, source_id, title, artist, url, license, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_id) DO UPDATE SET
            title = EXCLUDED.title, artist = EXCLUDED.artist, url = EXCLUDED.url,
            license = EXCLUDED.license, embedding = EXCLUDED.embedding
        """,
        (source, source_id, title, artist, url, license, embedding),
    )


def upsert_image(
    conn: psycopg.Connection,
    *,
    source: str,
    source_id: str,
    title: str,
    url: str,
    license: str,
    attribution: str,
    embedding: list[float],
) -> None:
    conn.execute(
        """
        INSERT INTO images (source, source_id, title, url, license, attribution, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_id) DO UPDATE SET
            title = EXCLUDED.title, url = EXCLUDED.url, license = EXCLUDED.license,
            attribution = EXCLUDED.attribution, embedding = EXCLUDED.embedding
        """,
        (source, source_id, title, url, license, attribution, embedding),
    )


def nearest_songs(conn: psycopg.Connection, embedding: list[float], limit: int = 5) -> list[Song]:
    rows = conn.execute(
        """
        SELECT id, title, artist, url, license, embedding <=> %s AS distance
        FROM songs ORDER BY distance LIMIT %s
        """,
        (Vector(embedding), limit),
    ).fetchall()
    return [Song(str(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]


def nearest_images(conn: psycopg.Connection, embedding: list[float], limit: int = 5) -> list[Image]:
    rows = conn.execute(
        """
        SELECT id, title, url, license, attribution, embedding <=> %s AS distance
        FROM images ORDER BY distance LIMIT %s
        """,
        (Vector(embedding), limit),
    ).fetchall()
    return [Image(str(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]


def counts(conn: psycopg.Connection) -> tuple[int, int]:
    songs = conn.execute("SELECT count(*) FROM songs").fetchone()[0]
    images = conn.execute("SELECT count(*) FROM images").fetchone()[0]
    return songs, images
