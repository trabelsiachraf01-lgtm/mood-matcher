"""The tiny in-memory catalog used before the real ingestion pipeline exists. Exactly two
items — one image, one song — since that's all the frontend's MediaKind supports as a match.
Replace with real Jamendo/Openverse ingestion later; this exists only to prove the
generate + embed + match loop end-to-end first.
"""

from __future__ import annotations

import io
import math
import struct
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path

import httpx

from src.core.embedding.embedder import embed_audio, embed_image


@dataclass(frozen=True)
class Fixture:
    id: str
    kind: str  # "image" | "song"
    title: str
    creator: str
    source: str
    license: str
    source_url: str


IMAGE_FIXTURE = Fixture(
    id="img-1",
    kind="image",
    title="Empty Highway at Dusk",
    creator="Mika Torres",
    source="Openverse",
    license="CC BY 2.0",
    source_url="https://picsum.photos/id/237/400/300",
)

# No real ingested songs yet, so a synthesized tone stands in for the catalog's one "song" —
# labeled honestly as a placeholder, not a real track.
SONG_FIXTURE = Fixture(
    id="song-1",
    kind="song",
    title="Test Tone (placeholder — not a real track)",
    creator="Synthesized locally",
    source="n/a",
    license="n/a",
    source_url="",
)


def _make_test_tone(seconds: float = 2.0, freq_hz: float = 440.0) -> bytes:
    sample_rate = 16000
    frames = int(seconds * sample_rate)
    samples = [int(32767 * math.sin(2 * math.pi * freq_hz * t / sample_rate)) for t in range(frames)]
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f"<{frames}h", *samples))
    return buffer.getvalue()


def build_catalog() -> list[tuple[Fixture, list[float]]]:
    """Embeds both fixtures once. Called at app startup, not import time — embedding needs
    the (lazily loaded) EBind model, and building the tone file needs a real temp path."""
    image_path = Path(tempfile.gettempdir()) / "mood_matcher_image_fixture.jpg"
    image_path.write_bytes(
        httpx.get(IMAGE_FIXTURE.source_url, timeout=30.0, follow_redirects=True).content
    )
    image_embedding = embed_image(str(image_path))

    tone_path = Path(tempfile.gettempdir()) / "mood_matcher_song_fixture.wav"
    tone_path.write_bytes(_make_test_tone())
    song_embedding = embed_audio(str(tone_path))

    return [(IMAGE_FIXTURE, image_embedding), (SONG_FIXTURE, song_embedding)]

