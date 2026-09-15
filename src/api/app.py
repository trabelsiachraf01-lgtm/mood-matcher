"""The real API: a thin HTTP layer over SuggestionService. All matching/captioning/embedding
logic lives in src/core/services — this module only translates HTTP <-> that service.
"""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import SuggestionResponse
from src.core.indexing.store import CatalogRepository, get_connection
from src.core.services.suggestion_service import SuggestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

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
    file: UploadFile | None = File(None),
) -> SuggestionResponse:
    service = SuggestionService(CatalogRepository(get_connection()))
    return service.suggest(input_mode=inputMode, text=text, file=file)
