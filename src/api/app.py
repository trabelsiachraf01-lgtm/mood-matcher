"""The real API: captioning + embedding + matching against the real pgvector-backed
catalog (src/core/indexing/store.py), populated by src/core/ingestion/*.
"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.captioning.captioner import caption_audio, caption_image
from src.core.embedding.embedder import embed_audio, embed_image, embed_text
from src.core.indexing.store import Image, Song, get_connection, nearest_images, nearest_songs
from src.core.media import download, transcode_to_wav

app = FastAPI(title="Mood Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    conn = get_connection()
    top_songs = nearest_songs(conn, query_embedding, limit=3)
    top_images = nearest_images(conn, query_embedding, limit=3)

    # pgvector's <=> is cosine *distance* — lower means more similar.
    candidates: list[tuple[Song | Image, Literal["song", "image"]]] = [
        (song, "song") for song in top_songs
    ] + [(image, "image") for image in top_images]
    candidates.sort(key=lambda pair: pair[0].distance)

    best, best_kind = candidates[0]
    related = candidates[1:4]

    if best_kind == "song":
        assert isinstance(best, Song)
        attribution = Attribution(creator=best.artist, source="Jamendo", license=best.license, sourceUrl=best.url)
        label = best.title
    else:
        assert isinstance(best, Image)
        attribution = Attribution(creator=best.attribution, source="Openverse", license=best.license, sourceUrl=best.url)
        label = best.title

    now_playing_song = top_songs[0] if top_songs else None

    return SuggestionResponse(
        caption=caption,
        matchedMedia=MatchedMedia(kind=best_kind, label=label),
        searchSummary=", ".join(request.moodTags) or "No mood filters set",
        attribution=attribution,
        relatedMatches=[
            RelatedMatch(
                id=item.id,
                title=item.title,
                creator=item.artist if isinstance(item, Song) else item.attribution,
                kind=kind,
            )
            for item, kind in related
        ],
        nowPlaying=NowPlaying(
            title=now_playing_song.title if now_playing_song else "—",
            artist=now_playing_song.artist if now_playing_song else "—",
            album="Mood Matcher catalog",
            currentTimeLabel="0:00",
            durationLabel="--:--",
            progressPercent=0,
            attribution=Attribution(
                creator=now_playing_song.artist if now_playing_song else "—",
                source="Jamendo",
                license=now_playing_song.license if now_playing_song else "",
                sourceUrl=now_playing_song.url if now_playing_song else "",
            ),
        ),
    )
