"""Loads EBind once and exposes embed_text/embed_image/embed_audio. This is the loading and
inference logic proven in tests/integration/test_embedding.py, extracted here for reuse now
that it's confirmed working (dtype cast to float32, points/Uni3D backbone skipped).
"""

from __future__ import annotations

import torch
from ebind import EBindModel, EBindProcessor

from src.core.config import EBIND_MODEL_ID

# "video" is a required base modality but shares the vision backbone with "image" — no extra
# download. Excluding "points" skips constructing the ~2GB Uni3D backbone, unused here.
MODALITIES = ["image", "video", "text", "audio"]

_model: EBindModel | None = None
_processor: EBindProcessor | None = None
_device: torch.device | None = None


def _load() -> None:
    global _model, _processor, _device
    if _model is not None:
        return
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model = EBindModel.from_pretrained(EBIND_MODEL_ID, modalities=MODALITIES).to(_device).eval()
    _processor = EBindProcessor.from_pretrained(EBIND_MODEL_ID)


def _embed(modality: str, value: str) -> list[float]:
    _load()
    assert _model is not None and _processor is not None and _device is not None
    with torch.inference_mode():
        batch = _processor({modality: [value]}, return_tensors="pt")
        batch.pop("return_tensors", None)
        batch = {k: v.to(_device) for k, v in batch.items()}
        output = _model.forward(**batch)[modality]
    return output.float().cpu().numpy()[0].tolist()


def embed_text(text: str) -> list[float]:
    return _embed("text", text)


def embed_image(image_path: str) -> list[float]:
    return _embed("image", image_path)


def embed_audio(audio_path: str) -> list[float]:
    return _embed("audio", audio_path)
