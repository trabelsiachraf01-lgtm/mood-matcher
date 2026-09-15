"""Mood captions for image and audio input, via OpenRouter (src/core/clients/openrouter).
"""

from __future__ import annotations

import base64

from src.core.clients.openrouter import chat
from src.core.config import AUDIO_MODEL, VISION_MODEL

_MOOD_PROMPT = (
    "In one vivid sentence, describe the mood and atmosphere this evokes — the feeling, "
    "not a literal list of what's in it. No preamble, just the sentence."
)


def caption_image(image_url: str) -> str:
    return chat(
        VISION_MODEL,
        [
            {"type": "text", "text": _MOOD_PROMPT},
            {"type": "image_url", "image_url": {"url": image_url}},
        ],
    )


def caption_audio(audio_bytes: bytes, audio_format: str) -> str:
    # OpenRouter requires base64-encoded audio — no plain-URL support, unlike image_url.
    encoded = base64.b64encode(audio_bytes).decode("utf-8")
    return chat(
        AUDIO_MODEL,
        [
            {"type": "text", "text": _MOOD_PROMPT},
            {"type": "input_audio", "input_audio": {"data": encoded, "format": audio_format}},
        ],
    )
