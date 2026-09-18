"""Business logic behind /suggestions: understand the input, find the closest real catalog
matches, and assemble the attributed response. Kept out of the API layer so it's testable
without spinning up FastAPI.
"""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import UploadFile

from src.api.schemas import Attribution, MatchedMedia, NowPlaying, SuggestionResponse
from src.core.indexing.store import CatalogRepository, Image, Song
from src.core.services.mood_analyzer import InputMode, MoodAnalyzer

logger = logging.getLogger(__name__)


class SuggestionService:
    """Every input mode gets the same pair of matches back: the closest real image (for the
    hero) and the closest real song (for the background player) — not just whichever of the
    two happens to be nearer, so a text or song query still surfaces a matching photo, and an
    image query still surfaces a matching song.
    """

    def __init__(self, repository: CatalogRepository, analyzer: MoodAnalyzer | None = None) -> None:
        self._repository = repository
        self._analyzer = analyzer or MoodAnalyzer()

    def suggest(
        self,
        *,
        input_mode: InputMode,
        text: str,
        file: UploadFile | None,
        song_source: Literal["catalog", "generate"] = "catalog",
    ) -> SuggestionResponse:
        analysis = self._analyzer.analyze(input_mode, text, file)
        image = next(iter(self._repository.nearest_images(analysis.embedding, limit=1)), None)
        # "generate" means the caller is about to make its own song via ElevenLabs — skip the
        # catalog lookup instead of fetching a match that's just going to be discarded.
        song = (
            next(iter(self._repository.nearest_songs(analysis.embedding, limit=1)), None)
            if song_source == "catalog"
            else None
        )

        logger.info(
            "match input_mode=%s song_source=%s image=%r image_distance=%s song=%r song_distance=%s",
            input_mode,
            song_source,
            image.title if image else None,
            f"{image.distance:.4f}" if image else "n/a",
            song.title if song else None,
            f"{song.distance:.4f}" if song else "n/a",
        )

        return SuggestionResponse(
            caption=analysis.caption,
            matchedMedia=self._matched_media(image),
            attribution=self._image_attribution(image),
            nowPlaying=self._now_playing(song),
        )

    @staticmethod
    def _matched_media(image: Image | None) -> MatchedMedia:
        if image is None:
            return MatchedMedia(kind="image", label="—", assetUrl="")
        return MatchedMedia(kind="image", label=image.title, assetUrl=image.asset_url or "")

    @staticmethod
    def _image_attribution(image: Image | None) -> Attribution:
        if image is None:
            return Attribution(creator="—", source="Openverse", license="", sourceUrl="")
        return Attribution(creator=image.attribution, source="Openverse", license=image.license, sourceUrl=image.url)

    @staticmethod
    def _now_playing(song: Song | None) -> NowPlaying:
        if song is None:
            return NowPlaying(
                title="—", artist="—", album="Hushtone catalog", assetUrl="",
                attribution=Attribution(creator="—", source="Jamendo", license="", sourceUrl=""),
            )
        return NowPlaying(
            title=song.title,
            artist=song.artist,
            album="Hushtone catalog",
            assetUrl=song.asset_url or "",
            attribution=Attribution(creator=song.artist, source="Jamendo", license=song.license, sourceUrl=song.url),
        )
