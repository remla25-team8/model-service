#!/bin/bash

echo "🔍 Test 1: Verify image does not contain model files"
echo "=================================================="

# Build image
echo "Building Docker image..."
docker build -t model-service-test .

# Check if image contains model files
echo -e "\nChecking files in image..."
docker run --rm model-service-test find /app -name "*.pkl" -o -name "*.joblib" | head -10

echo -e "\nChecking image size..."
docker images model-service-test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo -e "\n🔍 Test 2: Verify dynamic model loading"
echo "======================================"

# Test different model versions
echo "Testing model version 1..."
docker run --rm -e MODEL_VERSION=1 \
  -v $(pwd)/c1_BoW_Sentiment_Model.pkl:/app/models/c1_BoW_Sentiment_Model.pkl:ro \
  model-service-test python -c "
import os
print(f'MODEL_VERSION: {os.getenv(\"MODEL_VERSION\", \"Not set\")}')
print(f'VECTORIZER_PATH: {os.getenv(\"VECTORIZER_PATH\", \"Not set\")}')
from src.serve_model import HFModel
try:
    model = HFModel()
    print('✅ Model loaded successfully')
except Exception as e:
    print(f'❌ Model loading failed: {e}')
"

echo -e "\n🔍 Test 3: Verify local caching mechanism"
echo "========================================"

echo "First startup (will download model)..."
docker-compose up -d

sleep 10

echo "Checking service status..."
curl -s http://localhost:5000/health | jq . || echo "Service not ready"

echo -e "\nRestarting service (should use cache)..."
docker-compose restart

sleep 10

echo "Checking service status again..."
curl -s http://localhost:5000/health | jq . || echo "Service not ready"

echo -e "\nCleaning up..."
docker-compose down

echo -e "\n✅ Testing completed!" 