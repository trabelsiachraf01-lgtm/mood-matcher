"""Generates a short original track from a mood caption via ElevenLabs Music — an opt-in
alternative to the catalog-matched song, kept as its own call so it only runs (and costs
credits) when the user explicitly asks for it, never as part of /suggestions.
"""

from __future__ import annotations

import httpx
from fastapi import HTTPException

from src.core.clients import elevenlabs


class MusicGenerator:
    def generate(self, prompt: str) -> bytes:
        try:
            return elevenlabs.compose(prompt)
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=504, detail="Music generation timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=502, detail=f"ElevenLabs error: {exc.response.text}") from exc
