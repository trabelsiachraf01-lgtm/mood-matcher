"""Thin client for ElevenLabs' Music API — the one call in this project that generates
media instead of matching real, attributed media. See src/core/services/music_generator.py
for what uses it.
"""

from __future__ import annotations

import httpx

from src.core.config import (
    ELEVENLABS_API_BASE,
    ELEVENLABS_API_KEY,
    MUSIC_LENGTH_MS,
    MUSIC_TIMEOUT_SECONDS,
)


def compose(prompt: str) -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not set.")
    # music_length_ms is a hard cutoff, not a target — without this, the model often writes
    # a piece that's still building and gets truncated mid-phrase at the limit.
    full_prompt = (
        f"{prompt} A complete short piece, fully structured with an intro, a middle, and an "
        f"ending, written to conclude naturally within {MUSIC_LENGTH_MS // 1000} seconds — "
        "not a loop or an excerpt cut off mid-phrase."
    )
    response = httpx.post(
        ELEVENLABS_API_BASE,
        headers={"xi-api-key": ELEVENLABS_API_KEY},
        json={"prompt": full_prompt, "music_length_ms": MUSIC_LENGTH_MS, "model_id": "music_v2"},
        timeout=MUSIC_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.content
