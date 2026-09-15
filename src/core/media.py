"""Shared download/transcode helpers — used by both the live /suggestions endpoint
(src/api/app.py) and the ingestion clients (src/core/ingestion/), so this logic exists once.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import httpx

TRANSCODE_TIMEOUT_SECONDS = 30.0

_HEADERS = {
    # Some CDNs (Flickr's included) block httpx's default User-Agent outright — any normal
    # browser-like one works, so this exists purely to stop being fingerprinted as a bot.
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def download(url: str, suffix: str) -> Path:
    response = httpx.get(url, timeout=30.0, follow_redirects=True, headers=_HEADERS)
    response.raise_for_status()
    path = Path(tempfile.mktemp(suffix=suffix))
    path.write_bytes(response.content)
    return path


def transcode_to_wav(path: Path) -> Path:
    # torchcodec (ebind's audio decoder) is stricter than the ffmpeg CLI about malformed
    # tails/padding in arbitrary downloaded audio — normalizing to a clean WAV first avoids
    # relying on it to tolerate every format/quirk a source file might have.
    wav_path = path.with_suffix(".wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), "-ar", "16000", "-ac", "1", str(wav_path)],
        check=True,
        capture_output=True,
        timeout=TRANSCODE_TIMEOUT_SECONDS,
    )
    return wav_path
