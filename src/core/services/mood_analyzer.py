"""Turns a raw user input (text, or an uploaded image/audio file) into a mood caption plus
an embedding — the "understand what the user gave us" step, shared by every input mode.
"""

from __future__ import annotations

import base64
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fastapi import HTTPException, UploadFile

from src.core.captioning.captioner import caption_audio, caption_image
from src.core.embedding.embedder import embed_audio, embed_image, embed_text
from src.core.media import transcode_to_wav

InputMode = Literal["image", "song", "text"]


@dataclass(frozen=True)
class MoodAnalysis:
    caption: str
    embedding: list[float]


class MoodAnalyzer:
    """Captions and embeds one input, dispatching on its mode."""

    def analyze(self, input_mode: InputMode, text: str, file: UploadFile | None) -> MoodAnalysis:
        if input_mode == "text":
            return MoodAnalysis(caption=text, embedding=embed_text(text))
        if file is None:
            raise HTTPException(status_code=400, detail=f"No file uploaded for inputMode={input_mode}")
        if input_mode == "image":
            return self._analyze_image(file)
        return self._analyze_audio(file)

    def _analyze_image(self, file: UploadFile) -> MoodAnalysis:
        contents = file.file.read()
        tmp_path = self._write_temp(contents, file.filename, default_suffix=".jpg")
        mime_type = file.content_type or "image/jpeg"
        data_url = f"data:{mime_type};base64,{base64.b64encode(contents).decode()}"
        caption = caption_image(data_url)
        return MoodAnalysis(caption=caption, embedding=embed_image(str(tmp_path)))

    def _analyze_audio(self, file: UploadFile) -> MoodAnalysis:
        contents = file.file.read()
        tmp_path = self._write_temp(contents, file.filename, default_suffix=".mp3")
        audio_format = tmp_path.suffix.lstrip(".") or "mp3"
        caption = caption_audio(contents, audio_format=audio_format)
        wav_path = transcode_to_wav(tmp_path)
        return MoodAnalysis(caption=caption, embedding=embed_audio(str(wav_path)))

    @staticmethod
    def _write_temp(contents: bytes, filename: str | None, *, default_suffix: str) -> Path:
        suffix = Path(filename or "").suffix or default_suffix
        tmp_path = Path(tempfile.mktemp(suffix=suffix))
        tmp_path.write_bytes(contents)
        return tmp_path
