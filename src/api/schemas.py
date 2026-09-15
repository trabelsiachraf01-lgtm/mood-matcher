"""Response shapes for /suggestions — the API contract with the frontend."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Attribution(BaseModel):
    creator: str
    source: str
    license: str
    sourceUrl: str


class MatchedMedia(BaseModel):
    kind: Literal["image", "song"]
    label: str
    assetUrl: str


class NowPlaying(BaseModel):
    title: str
    artist: str
    album: str
    assetUrl: str
    attribution: Attribution


class SuggestionResponse(BaseModel):
    caption: str
    matchedMedia: MatchedMedia
    attribution: Attribution
    nowPlaying: NowPlaying
