"""Proves EBind loads and produces sensible embeddings across modalities: same-mood text
pairs, an image against a matching vs. mismatched caption, and a synthesized audio tone
against a matching vs. mismatched caption. Real model weights, real inference — integration,
not unit.
"""

import io
import math
import struct
import wave
from pathlib import Path

import httpx
import torch
from ebind import EBindModel, EBindProcessor

# "video" is a required base modality but shares the vision backbone with "image" — no extra
# download. Excluding "points" skips the model ever constructing (and downloading) the ~2GB
# Uni3D backbone, which this project has no use for.
MODALITIES = ["image", "video", "text", "audio"]

MOOD_SENTENCES = {
    "melancholy": [
        "Rain streaks down the window on a grey, quiet afternoon.",
        "An empty train platform at dusk, everyone already gone.",
    ],
    "upbeat": [
        "Confetti and bass drops at a packed rooftop party.",
        "Sprinting down the beach laughing in the bright noon sun.",
    ],
}

IMAGE_URL = "https://picsum.photos/id/237/400/300"  # a well-known fixed Lorem Picsum photo (a dog)
IMAGE_CAPTIONS = [
    "A fluffy puppy resting on a wooden floor.",
    "A businessman giving a presentation in a conference room.",
]

AUDIO_CAPTIONS = [
    "A high-pitched electronic alarm tone.",
    "A full orchestra performing a symphony.",
]


def _load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EBindModel.from_pretrained("encord-team/ebind-full", modalities=MODALITIES)
    model = model.to(device).eval()
    processor = EBindProcessor.from_pretrained("encord-team/ebind-full")
    return model, processor, device


def make_test_tone(seconds: float = 2.0, freq_hz: float = 1000.0) -> bytes:
    """A synthesized alarm-pitch sine wave, generated locally so this test doesn't depend on
    any external file host staying reachable."""
    sample_rate = 16000
    frames = int(seconds * sample_rate)
    samples = [int(32767 * math.sin(2 * math.pi * freq_hz * t / sample_rate)) for t in range(frames)]

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f"<{frames}h", *samples))
    return buffer.getvalue()


def test_ebind_separates_moods_text_to_text():
    model, processor, device = _load_model()

    labels = [mood for mood, sentences in MOOD_SENTENCES.items() for _ in sentences]
    texts = [sentence for sentences in MOOD_SENTENCES.values() for sentence in sentences]

    with torch.inference_mode():
        batch = processor({"text": texts}, return_tensors="pt")
        batch.pop("return_tensors", None)
        batch = {k: v.to(device) for k, v in batch.items()}
        embeddings = model.forward(**batch)["text"]

    similarity = (embeddings @ embeddings.T).float().cpu().numpy()
    print("text-to-text cosine similarity:")
    for label, row in zip(labels, similarity, strict=True):
        print(f"  {label:>12} | " + " ".join(f"{v:.2f}" for v in row))

    same_mood = (similarity[0, 1] + similarity[2, 3]) / 2
    cross_mood = similarity[0, 2:].mean()
    print(f"avg same-mood similarity:  {same_mood:.3f}")
    print(f"avg cross-mood similarity: {cross_mood:.3f}")
    assert same_mood > cross_mood


def test_ebind_matches_image_to_text(tmp_path: Path):
    model, processor, device = _load_model()

    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(httpx.get(IMAGE_URL, timeout=30.0, follow_redirects=True).content)

    with torch.inference_mode():
        batch = processor({"image": [str(image_path)], "text": IMAGE_CAPTIONS}, return_tensors="pt")
        batch.pop("return_tensors", None)
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model.forward(**batch)

    similarity = (outputs["image"] @ outputs["text"].T).float().cpu().numpy()[0]
    print("image-to-text cosine similarity:")
    for caption, score in zip(IMAGE_CAPTIONS, similarity, strict=True):
        print(f"  {score:.3f}  {caption}")

    assert similarity[0] > similarity[1]  # the puppy caption should win


def test_ebind_matches_audio_to_text(tmp_path: Path):
    model, processor, device = _load_model()

    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(make_test_tone())

    with torch.inference_mode():
        batch = processor({"audio": [str(audio_path)], "text": AUDIO_CAPTIONS}, return_tensors="pt")
        batch.pop("return_tensors", None)
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model.forward(**batch)

    similarity = (outputs["audio"].float() @ outputs["text"].float().T).cpu().numpy()[0]
    print("audio-to-text cosine similarity:")
    for caption, score in zip(AUDIO_CAPTIONS, similarity, strict=True):
        print(f"  {score:.3f}  {caption}")

    assert similarity[0] > similarity[1]  # the alarm-tone caption should win
