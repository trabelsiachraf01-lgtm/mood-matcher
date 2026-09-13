"""Proves the OpenRouter-hosted Qwen3-VL (image) and Gemini Flash (audio) calls work
end-to-end. Requires OPENROUTER_API_KEY (get one at https://openrouter.ai) in the environment.
Real network calls, real billing — integration, not unit.
"""

import io
import math
import os
import struct
import wave

import pytest
from dotenv import load_dotenv

from src.core.captioning.captioner import caption_audio, caption_image

load_dotenv()

# A well-known fixed Lorem Picsum photo (a dog) — deterministic, nothing for us to host.
IMAGE_URL = "https://picsum.photos/id/237/400/300"

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"), reason="OPENROUTER_API_KEY not set"
)


def make_test_tone(seconds: float = 2.0, freq_hz: float = 440.0) -> bytes:
    """A synthesized sine-wave WAV, generated locally so this test doesn't depend on any
    external file host staying reachable."""
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


def test_caption_image_returns_text():
    caption = caption_image(IMAGE_URL)
    print(f"image caption: {caption}")
    assert caption.strip()


def test_caption_audio_returns_text():
    caption = caption_audio(make_test_tone(), audio_format="wav")
    print(f"audio caption: {caption}")
    assert caption.strip()
