-- Real ingestion catalog, replacing the in-memory fixture in src/core/embedding/fixtures.py.
-- Applied directly with psql — no ORM, no migration tool, since the schema is still this
-- small and this is the first real version of it.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS songs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL DEFAULT 'jamendo',
    source_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    url TEXT NOT NULL,
    license TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL DEFAULT 'openverse',
    source_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    license TEXT NOT NULL,
    attribution TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS songs_embedding_idx ON songs
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS images_embedding_idx ON images
    USING hnsw (embedding vector_cosine_ops);
