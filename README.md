Production-ready Flask API serving a Hugging Face sentiment analysis model with integrated preprocessing from `lib-ml`.

## 📌 Features

- **Preprocessing Pipeline**: Integrated `lib-ml` for consistent text transformation
- **Model Serving**: Hosts Hugging Face model with version support
- **REST API**: 
  - `/predict` - Full sentiment analysis pipeline
  - `/dumbpredict` - Mock endpoint for testing
  - `/health` - Service health check
- **Documentation**: Auto-generated Swagger UI at `/api/docs`
- **Configurable**: Environment variables for all critical parameters

## 🚀 Deployment

### Docker (Recommended)
```bash
docker run -p 5000:5000 \
  -e PORT=5000 \
  -e FLASK_ENV=production \
  ghcr.io/remla25-team8/model-service:latest
