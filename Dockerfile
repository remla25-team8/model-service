# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ .

# Environment variables (with your specified paths)
ENV FLASK_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0 \
    MODEL_SERVICE_ENDPOINT=http://0.0.0.0:8080 \
    MODEL_PATH=/app/model.joblib \
    VECTORIZER_PATH=/app/vectorizer.joblib \
    PATH=/root/.local/bin:$PATH

# Download model files with fallback URLs and error handling
RUN wget ${MODEL_URL:-https://storage.example.com/models/v1.0/model.joblib} -O ${MODEL_PATH} && \
    wget ${VECTORIZER_URL:-https://storage.example.com/models/v1.0/vectorizer.joblib} -O ${VECTORIZER_PATH} || \
    (echo "Failed to download model files" && exit 1)

EXPOSE ${PORT}
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--workers", "4", "serve_model:app"]