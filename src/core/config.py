"""Single place environment variables and model names get read from — nothing else in this
project should call os.environ or hardcode a model id directly.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1/chat/completions")


VISION_MODEL = os.environ.get("VISION_MODEL", "google/gemini-3.5-flash-lite")
AUDIO_MODEL = os.environ.get("AUDIO_MODEL", "google/gemini-3.5-flash-lite")
TEXT_MODEL = os.environ.get("TEXT_MODEL", "google/gemini-3.5-flash-lite")

EBIND_MODEL_ID = os.environ.get("EBIND_MODEL_ID", "encord-team/ebind-full")

# Hard caps so one slow OpenRouter call or a stuck local inference can't hang a request
# forever — /suggestions fails fast with a 504 instead.
LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "20"))
EMBED_TIMEOUT_SECONDS = float(os.environ.get("EMBED_TIMEOUT_SECONDS", "15"))

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://mood_matcher:mood_matcher@localhost:5432/mood_matcher"
)

JAMENDO_CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID")

# Eleven Music — opt-in generation (see src/core/clients/elevenlabs.py), not on the default
# /suggestions path, so a slow or unset key never blocks a normal match.
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_API_BASE = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io/v1/music/compose")
# ElevenLabs accepts 3,000-600,000ms; kept short (30s) since generation latency scales with
# output length and this runs synchronously in the wizard, not in the background.
MUSIC_LENGTH_MS = int(os.environ.get("MUSIC_LENGTH_MS", "30000"))
MUSIC_TIMEOUT_SECONDS = float(os.environ.get("MUSIC_TIMEOUT_SECONDS", "60"))

