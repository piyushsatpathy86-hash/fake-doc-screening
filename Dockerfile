FROM python:3.10-slim

# libgl1 + libglib2.0-0 are required or `import cv2` crashes with
# "libGL.so.1: cannot open shared object file" on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download the DeepFace/VGG-Face weights at BUILD time, not first request.
# Without this, your first user request downloads ~500MB and almost
# certainly blows past Cloud Run's request timeout.
RUN python -c "from deepface import DeepFace; DeepFace.build_model('VGG-Face')"

ENV PORT=8080
EXPOSE 8080

# Shell form (not JSON array form) so $PORT actually gets expanded.
# Cloud Run injects PORT itself — never hardcode a port number here.
CMD exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT