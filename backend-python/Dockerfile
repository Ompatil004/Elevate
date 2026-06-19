FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies needed for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and other directories
COPY app/ ./app/
COPY data/ ./data/
COPY models/ ./models/
COPY server.py ./

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
