# Build stage
FROM python:3.10-slim AS builder

# Install system dependencies including git
RUN apt-get update && \
apt-get install -y --no-install-recommends git && \
rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Install all dependencies (including gunicorn)
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && \
apt-get install -y --no-install-recommends wget && \
rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python packages and gunicorn from builder
COPY --from=builder /root/.local /root/.local

# Ensure .local/bin is in PATH
ENV PATH=/root/.local/bin:$PATH

COPY src/ .

# Environment variables
ENV FLASK_ENV=production \
PORT=8080 \
HOST=0.0.0.0 \
MODEL_SERVICE_ENDPOINT=http://0.0.0.0:8080 \
MODEL_PATH=/app/model.joblib \
VECTORIZER_PATH=/app/vectorizer.joblib

# Download assets with fallback
RUN wget ${MODEL_URL:-https://storage.example.com/models/v1.0/model.joblib} -O ${MODEL_PATH} && \
wget ${VECTORIZER_URL:-https://storage.example.com/models/v1.0/vectorizer.joblib} -O ${VECTORIZER_PATH} || \
(echo "Warning: Failed to download model files" && touch ${MODEL_PATH} ${VECTORIZER_PATH})

EXPOSE ${PORT}
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 4 serve_model:app"]

ARG VERSION=latest
LABEL org.opencontainers.image.version=$VERSION