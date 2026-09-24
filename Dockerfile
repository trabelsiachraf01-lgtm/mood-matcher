FROM python:3.14-slim

# ffmpeg is what torchcodec needs for audio decoding — on Linux this just works, no
# DYLD_LIBRARY_PATH hack required (that was a macOS-only quirk of the local setup).
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# CPU-only torch build — the plain PyPI wheel pulls CUDA deps that are dead weight on a
# dev machine with no GPU, and multiply the image size several times over.
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
