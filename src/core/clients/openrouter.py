"""Thin client for OpenRouter's chat completions API — the one trusted aggregator this
project calls through for every hosted model. See src/core/captioning for what uses it.
"""

from __future__ import annotations

import httpx

from src.core.config import LLM_TIMEOUT_SECONDS, OPENROUTER_API_BASE, OPENROUTER_API_KEY

_BASE_URL = OPENROUTER_API_BASE

def chat(model: str, content: list[dict]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")
    response = httpx.post(
        _BASE_URL,
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": model, "messages": [{"role": "user", "content": content}]},
        timeout=LLM_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
