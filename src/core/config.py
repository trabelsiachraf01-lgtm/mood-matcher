"""Single place environment variables and model names get read from — nothing else in this
project should call os.environ or hardcode a model id directly.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1/chat/completions")


VISION_MODEL = os.environ.get("VISION_MODEL", "qwen/qwen3-vl-32b-instruct")
AUDIO_MODEL = os.environ.get("AUDIO_MODEL", "google/gemini-2.5-flash")

EBIND_MODEL_ID = os.environ.get("EBIND_MODEL_ID", "encord-team/ebind-full")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://mood_matcher:mood_matcher@localhost:5432/mood_matcher"
)

JAMENDO_CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID")

