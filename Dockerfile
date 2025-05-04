# Build stage
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Install runtime deps (git for lib-ml, wget for model download)
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ .

# Environment variables (with defaults)
ENV PORT=8080
ENV MODEL_URL="https://storage.example.com/models/v1.0/model.joblib"
ENV VECTORIZER_URL="https://storage.example.com/models/v1.0/vectorizer.joblib"
ENV HOST="0.0.0.0"

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Download model and vectorizer on startup
RUN wget $MODEL_URL -O model.joblib && \
    wget $VECTORIZER_URL -O vectorizer.joblib

EXPOSE $PORT
CMD ["gunicorn", "--bind", "$HOST:$PORT", "serve_model:app"]