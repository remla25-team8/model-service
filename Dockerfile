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
PORT=5000 \
HOST=0.0.0.0 \
MODEL_SERVICE_ENDPOINT=http://0.0.0.0:5000 \
MODEL_VERSION=1 \
VECTORIZER_PATH=/app/models/c1_BoW_Sentiment_Model.pkl

# Create model directory for volume mounting
RUN mkdir -p /app/models

EXPOSE ${PORT}
# CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 4 serve_model:app"]
CMD ["python", "serve_model.py"]

ARG VERSION=latest
LABEL org.opencontainers.image.version=$VERSION