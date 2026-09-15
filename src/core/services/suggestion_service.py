"""Business logic behind /suggestions: understand the input, find the closest real catalog
matches, and assemble the attributed response. Kept out of the API layer so it's testable
without spinning up FastAPI.
"""

from __future__ import annotations

from typing import Literal

from fastapi import UploadFile

from src.api.schemas import Attribution, MatchedMedia, NowPlaying, RelatedMatch, SuggestionResponse
from src.core.indexing.store import CatalogRepository, Image, Song
from src.core.services.mood_analyzer import InputMode, MoodAnalyzer

Candidate = tuple[Song | Image, Literal["song", "image"]]


class SuggestionService:
    def __init__(self, repository: CatalogRepository, analyzer: MoodAnalyzer | None = None) -> None:
        self._repository = repository
        self._analyzer = analyzer or MoodAnalyzer()

    def suggest(self, *, input_mode: InputMode, text: str, file: UploadFile | None) -> SuggestionResponse:
        analysis = self._analyzer.analyze(input_mode, text, file)
        candidates = self._rank_candidates(analysis.embedding)

        best, best_kind = candidates[0]
        related = candidates[1:4]
        now_playing_song = next((c for c, kind in candidates if kind == "song"), None)

        return SuggestionResponse(
            caption=analysis.caption,
            matchedMedia=MatchedMedia(kind=best_kind, label=best.title, assetUrl=best.asset_url or ""),
            attribution=self._attribution_for(best, best_kind),
            relatedMatches=[
                RelatedMatch(id=item.id, title=item.title, creator=self._creator(item), kind=kind, url=item.url)
                for item, kind in related
            ],
            nowPlaying=self._now_playing(now_playing_song),
        )

    def _rank_candidates(self, embedding: list[float]) -> list[Candidate]:
        songs: list[Candidate] = [(song, "song") for song in self._repository.nearest_songs(embedding, limit=3)]
        images: list[Candidate] = [(image, "image") for image in self._repository.nearest_images(embedding, limit=3)]
        # pgvector's <=> is cosine *distance* — lower means more similar.
        return sorted(songs + images, key=lambda pair: pair[0].distance)

    @staticmethod
    def _creator(item: Song | Image) -> str:
        return item.artist if isinstance(item, Song) else item.attribution

    def _attribution_for(self, item: Song | Image, kind: Literal["song", "image"]) -> Attribution:
        if kind == "song":
            assert isinstance(item, Song)
            return Attribution(creator=item.artist, source="Jamendo", license=item.license, sourceUrl=item.url)
        assert isinstance(item, Image)
        return Attribution(creator=item.attribution, source="Openverse", license=item.license, sourceUrl=item.url)

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
