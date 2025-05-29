# Model Service Repository README

## Assignment 5: Istio Service Mesh (Member 1 Contributions)

This repository contains the *Restaurant Sentiment Analysis* model service, providing ML predictions via a REST API with a Hugging Face model. For Assignment 5, Member 1 modified the service to support **Traffic Management** requirements at the **Excellent** level, specifically Sticky Sessions and version consistency, while preserving existing functionality (preprocessing, `/health`, `/dumbpredict`, Swagger).

### Changes Made

1. **Sticky Sessions Support**:
   - Updated `src/serve_model.py` in the `/predict` route to log the `x-user-id` header for debugging Istio Sticky Sessions routing.
   - Added `x-user-id` to Swagger documentation.
   - Maintained Hugging Face model integration, preprocessing, and other endpoints (`/health`, `/dumbpredict`).

2. **Version Consistency**:
   - Updated `requirements.txt` to ensure `lib-ml==1.19.0` and `lib-version==0.9.5` match `app` (versions assumed; confirm with A1).

### Testing Instructions

1. **Prerequisites**:
   - Deploy the Helm chart from the `operation` repository:
     ```bash
     helm install myapp ./helm/myapp -n default
     ```
   - Verify `app` forwards requests to `model-service` (`http://model-service:8080/predict`).
   - Add `192.168.56.90 app.local` to `/etc/hosts`.

2. **Automated Testing**:
   ```bash
   bash helm/myapp/tests/sticky-session-test.sh
   ```
   - **Expected Output**:
     - Second loop: Logs show `x-user-id: test-user` for v2-routed requests.
     - Responses include `sentiment`, `confidence`, `processed_review`.

3. **Manual Testing**:
   ```bash
   # Test via app
   curl -H "Host: app.local" -H "x-user-id: test-user" http://192.168.56.90/analyze -d '{"review": "Great food!"}' -H "Content-Type: application/json"
   
   # Direct test to model-service (optional)
   curl http://<model-service>:8080/predict -d '{"review": "Great food!"}' -H "x-user-id: test-user" -H "Content-Type: application/json"
   ```
   - **Expected Output**: JSON response with `{"sentiment": "...", "confidence": ..., "processed_review": "..."}`.

### Verification Methods

1. **Sticky Sessions**:
   - Check logs: `kubectl logs -l app=model-service -n default` (look for `Received request with x-user-id: test-user`).
   - Confirm `x-user-id: test-user` requests are logged for v2 routes from `app`.

2. **Version Consistency**:
   - Compare `requirements.txt` with `app/requirements.txt` for `lib-ml==1.19.0` and `lib-version==0.9.5`.
   - Run `kubectl exec -it <model-service-pod> -n default -- pip list` to verify versions.

3. **Functionality**:
   - Test endpoints: Ensure `/predict`, `/health`, and `/dumbpredict` respond correctly.
   - Verify preprocessing and Hugging Face model predictions are unchanged.
   - Confirm Swagger UI works: `http://<model-service>:8080/api/docs`.

If predictions fail or headers are missing, check Flask logs or `app`’s header forwarding logic.