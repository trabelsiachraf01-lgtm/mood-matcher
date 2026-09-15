"""The real API: a thin HTTP layer over SuggestionService. All matching/captioning/embedding
logic lives in src/core/services — this module only translates HTTP <-> that service.
"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import SuggestionResponse
from src.core.indexing.store import CatalogRepository, get_connection
from src.core.services.suggestion_service import SuggestionService

app = FastAPI(title="Hushtone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/suggestions")
def suggest(
    inputMode: Literal["image", "song", "text"] = Form(...),
    text: str = Form(""),
    moodTags: str = Form(""),
    energy: int = Form(50),
    file: UploadFile | None = File(None),
) -> SuggestionResponse:
    service = SuggestionService(CatalogRepository(get_connection()))
    mood_tags = [tag for tag in moodTags.split(",") if tag]
    return service.suggest(input_mode=inputMode, text=text, mood_tags=mood_tags, file=file)
