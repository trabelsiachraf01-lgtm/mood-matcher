"""Turns a raw user input (text, or an uploaded image/audio file) into a mood caption plus
an embedding — the "understand what the user gave us" step, shared by every input mode.
"""

from __future__ import annotations

import base64
import logging
import tempfile
import time
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeVar

import httpx
from fastapi import HTTPException, UploadFile

from src.core.captioning.captioner import caption_audio, caption_image
from src.core.config import EMBED_TIMEOUT_SECONDS, LLM_TIMEOUT_SECONDS
from src.core.embedding.embedder import embed_audio, embed_image, embed_text
from src.core.media import TRANSCODE_TIMEOUT_SECONDS, transcode_to_wav

InputMode = Literal["image", "song", "text"]

logger = logging.getLogger(__name__)

T = TypeVar("T")

# httpx already enforces LLM_TIMEOUT_SECONDS on the caption call itself; this margin just
# covers thread handoff so the two timeouts don't race each other.
_SAFETY_MARGIN_SECONDS = 5.0


def _await(future: Future[T], timeout: float, what: str) -> T:
    """Caps how long one step of the pipeline can block, so a stuck call fails fast (504)
    instead of hanging the request indefinitely. Logs how long the step actually took, so
    captioning (network) and embedding (local) latency can be compared directly in the logs.
    """
    started = time.monotonic()
    try:
        result = future.result(timeout=timeout)
    except (FutureTimeoutError, httpx.TimeoutException) as exc:
        raise HTTPException(status_code=504, detail=f"{what} timed out after {timeout:.0f}s") from exc
    logger.info("%s took=%.2fs", what, time.monotonic() - started)
    return result


@dataclass(frozen=True)
class MoodAnalysis:
    caption: str
    embedding: list[float]


class MoodAnalyzer:
    """Captions and embeds one input, dispatching on its mode."""

    def analyze(self, input_mode: InputMode, text: str, file: UploadFile | None) -> MoodAnalysis:
        started = time.monotonic()
        if input_mode == "text":
            result = self._analyze_text(text)
        else:
            if file is None:
                raise HTTPException(status_code=400, detail=f"No file uploaded for inputMode={input_mode}")
            result = self._analyze_image(file) if input_mode == "image" else self._analyze_audio(file)
        logger.info("analyze mode=%s took=%.2fs", input_mode, time.monotonic() - started)
        return result

    def _analyze_text(self, text: str) -> MoodAnalysis:
        with ThreadPoolExecutor(max_workers=1) as pool:
            embedding = _await(pool.submit(embed_text, text), EMBED_TIMEOUT_SECONDS, "embedding")
        return MoodAnalysis(caption=text, embedding=embedding)

    def _analyze_image(self, file: UploadFile) -> MoodAnalysis:
        contents = file.file.read()
        tmp_path = self._write_temp(contents, file.filename, default_suffix=".jpg")
        mime_type = file.content_type or "image/jpeg"
        data_url = f"data:{mime_type};base64,{base64.b64encode(contents).decode()}"

        # Captioning (a network call to a hosted LLM) and embedding (local EBind inference)
        # don't depend on each other — run them concurrently instead of paying their sum.
        with ThreadPoolExecutor(max_workers=2) as pool:
            caption_future = pool.submit(caption_image, data_url)
            embedding_future = pool.submit(embed_image, str(tmp_path))
            caption = _await(caption_future, LLM_TIMEOUT_SECONDS + _SAFETY_MARGIN_SECONDS, "captioning")
            embedding = _await(embedding_future, EMBED_TIMEOUT_SECONDS, "embedding")
        return MoodAnalysis(caption=caption, embedding=embedding)

    def _analyze_audio(self, file: UploadFile) -> MoodAnalysis:
        contents = file.file.read()
        tmp_path = self._write_temp(contents, file.filename, default_suffix=".mp3")
        audio_format = tmp_path.suffix.lstrip(".") or "mp3"

        # Captioning (network) and transcoding (local ffmpeg) don't depend on each other;
        # embedding needs the transcoded wav, so it waits on that one.
        with ThreadPoolExecutor(max_workers=2) as pool:
            caption_future = pool.submit(caption_audio, contents, audio_format=audio_format)
            transcode_future = pool.submit(transcode_to_wav, tmp_path)
            wav_path = _await(transcode_future, TRANSCODE_TIMEOUT_SECONDS + _SAFETY_MARGIN_SECONDS, "transcoding")

            embedding_future = pool.submit(embed_audio, str(wav_path))
            embedding = _await(embedding_future, EMBED_TIMEOUT_SECONDS, "embedding")
            caption = _await(caption_future, LLM_TIMEOUT_SECONDS + _SAFETY_MARGIN_SECONDS, "captioning")
        return MoodAnalysis(caption=caption, embedding=embedding)

    @staticmethod
    def _write_temp(contents: bytes, filename: str | None, *, default_suffix: str) -> Path:
        suffix = Path(filename or "").suffix or default_suffix
        tmp_path = Path(tempfile.mktemp(suffix=suffix))
        tmp_path.write_bytes(contents)
        return tmp_path
