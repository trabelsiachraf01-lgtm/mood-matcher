"""The real API: captioning + embedding + matching against the real pgvector-backed
catalog (src/core/indexing/store.py), populated by src/core/ingestion/*.

Takes multipart form data, not JSON — image/song modes upload a real file (no URL involved).
"""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.core.captioning.captioner import caption_audio, caption_image
from src.core.embedding.embedder import embed_audio, embed_image, embed_text
from src.core.indexing.store import Image, Song, get_connection, nearest_images, nearest_songs
from src.core.media import transcode_to_wav

app = FastAPI(title="Hushtone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Attribution(BaseModel):
    creator: str
    source: str
    license: str
    sourceUrl: str


class MatchedMedia(BaseModel):
    kind: Literal["image", "song"]
    label: str
    assetUrl: str


class RelatedMatch(BaseModel):
    id: str
    title: str
    creator: str
    kind: Literal["image", "song"]
    url: str


class NowPlaying(BaseModel):
    title: str
    artist: str
    album: str
    assetUrl: str
    attribution: Attribution


class SuggestionResponse(BaseModel):
    caption: str
    matchedMedia: MatchedMedia
    searchSummary: str
    attribution: Attribution
    relatedMatches: list[RelatedMatch]
    nowPlaying: NowPlaying


def _caption_and_embed(
    input_mode: Literal["image", "song", "text"], text: str, file: UploadFile | None
) -> tuple[str, list[float]]:
    if input_mode == "text":
        return text, embed_text(text)

    if file is None:
        raise HTTPException(status_code=400, detail=f"No file uploaded for inputMode={input_mode}")

    contents = file.file.read()
    default_suffix = ".jpg" if input_mode == "image" else ".mp3"
    suffix = Path(file.filename or "").suffix or default_suffix
    tmp_path = Path(tempfile.mktemp(suffix=suffix))
    tmp_path.write_bytes(contents)

    if input_mode == "image":
        mime_type = file.content_type or "image/jpeg"
        data_url = f"data:{mime_type};base64,{base64.b64encode(contents).decode()}"
        caption = caption_image(data_url)
        return caption, embed_image(str(tmp_path))

    audio_format = suffix.lstrip(".") or "mp3"
    caption = caption_audio(contents, audio_format=audio_format)
    wav_path = transcode_to_wav(tmp_path)
    return caption, embed_audio(str(wav_path))


@app.post("/suggestions")
def suggest(
    inputMode: Literal["image", "song", "text"] = Form(...),
    text: str = Form(""),
    moodTags: str = Form(""),
    energy: int = Form(50),
    file: UploadFile | None = File(None),
) -> SuggestionResponse:
    mood_tags = [tag for tag in moodTags.split(",") if tag]
    caption, query_embedding = _caption_and_embed(inputMode, text, file)

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
        matchedMedia=MatchedMedia(kind=best_kind, label=label, assetUrl=best.asset_url or ""),
        searchSummary=", ".join(mood_tags) or "No mood filters set",
        attribution=attribution,
        relatedMatches=[
            RelatedMatch(
                id=item.id,
                title=item.title,
                creator=item.artist if isinstance(item, Song) else item.attribution,
                kind=kind,
                url=item.url,
            )
            for item, kind in related
        ],
        nowPlaying=NowPlaying(
            title=now_playing_song.title if now_playing_song else "—",
            artist=now_playing_song.artist if now_playing_song else "—",
            album="Hushtone catalog",
            assetUrl=(now_playing_song.asset_url or "") if now_playing_song else "",
            attribution=Attribution(
                creator=now_playing_song.artist if now_playing_song else "—",
                source="Jamendo",
                license=now_playing_song.license if now_playing_song else "",
                sourceUrl=now_playing_song.url if now_playing_song else "",
            ),
        ),
    )
