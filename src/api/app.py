"""Minimal API hooking the frontend up to the real pipeline (captioning + embedding),
matched against a 2-item in-memory catalog — one image, one placeholder song — since the
real ingestion pipeline doesn't exist yet. This exists to prove the full loop end-to-end
before building that pipeline, not to be a real product backend.
"""

from __future__ import annotations

import math
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.captioning.captioner import caption_audio, caption_image
from src.core.embedding.embedder import embed_audio, embed_image, embed_text
from src.core.embedding.fixtures import Fixture, build_catalog
from src.core.media import download, transcode_to_wav

app = FastAPI(title="Mood Matcher (dev)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_catalog: list[tuple[Fixture, list[float]]] = []


@app.on_event("startup")
def _startup() -> None:
    global _catalog
    _catalog = build_catalog()


class SuggestionRequest(BaseModel):
    inputMode: Literal["image", "song", "text"]
    inputValue: str
    moodTags: list[str] = []
    energy: int = 50


class Attribution(BaseModel):
    creator: str
    source: str
    license: str
    sourceUrl: str


class MatchedMedia(BaseModel):
    kind: Literal["image", "song"]
    label: str


class RelatedMatch(BaseModel):
    id: str
    title: str
    creator: str
    kind: Literal["image", "song"]


class NowPlaying(BaseModel):
    title: str
    artist: str
    album: str
    currentTimeLabel: str
    durationLabel: str
    progressPercent: int
    attribution: Attribution


class SuggestionResponse(BaseModel):
    caption: str
    matchedMedia: MatchedMedia
    searchSummary: str
    attribution: Attribution
    relatedMatches: list[RelatedMatch]
    nowPlaying: NowPlaying


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _caption_and_embed(request: SuggestionRequest) -> tuple[str, list[float]]:
    if request.inputMode == "text":
        return request.inputValue, embed_text(request.inputValue)

    if request.inputMode == "image":
        caption = caption_image(request.inputValue)
        image_path = download(request.inputValue, ".jpg")
        return caption, embed_image(str(image_path))

    audio_path = download(request.inputValue, ".mp3")
    caption = caption_audio(audio_path.read_bytes(), audio_format="mp3")
    wav_path = transcode_to_wav(audio_path)
    return caption, embed_audio(str(wav_path))


@app.post("/suggestions")
def suggest(request: SuggestionRequest) -> SuggestionResponse:
    caption, query_embedding = _caption_and_embed(request)

    ranked = sorted(_catalog, key=lambda item: _cosine(query_embedding, item[1]), reverse=True)
    best_fixture, _ = ranked[0]
    other_fixture, _ = ranked[1]

    attribution = Attribution(
        creator=best_fixture.creator,
        source=best_fixture.source,
        license=best_fixture.license,
        sourceUrl=best_fixture.source_url,
    )

    return SuggestionResponse(
        caption=caption,
        matchedMedia=MatchedMedia(kind=best_fixture.kind, label=best_fixture.title),  # type: ignore[arg-type]
        searchSummary=", ".join(request.moodTags) or "No mood filters set",
        attribution=attribution,
        relatedMatches=[
            RelatedMatch(
                id=other_fixture.id,
                title=other_fixture.title,
                creator=other_fixture.creator,
                kind=other_fixture.kind,  # type: ignore[arg-type]
            )
        ],
        nowPlaying=NowPlaying(
            title="Test Tone",
            artist="Synthesized locally",
            album="Mood Matcher fixtures",
            currentTimeLabel="0:00",
            durationLabel="0:02",
            progressPercent=0,
            attribution=Attribution(
                creator="Synthesized locally",
                source="Local test asset",
                license="No real track yet",
                sourceUrl="",
            ),
        ),
    )
