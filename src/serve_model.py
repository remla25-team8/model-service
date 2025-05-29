"""
Production-ready Flask API with integrated preprocessing and hugging face model
"""

from flask import Flask, jsonify, request
from flasgger import Swagger
from lib_ml.preprocessor import Preprocessor
import logging
import os
import json
import joblib
from huggingface_hub import hf_hub_download

app = Flask(__name__)

# Configure from environment with defaults
app.config.update({
    'ENV': os.getenv('FLASK_ENV', 'production'),
    'DEBUG': os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
    'HOST': os.getenv('HOST', '0.0.0.0'),
    'PORT': int(os.getenv('PORT', 5000)),
    'MODEL_SERVICE_ENDPOINT': os.getenv('MODEL_SERVICE_ENDPOINT', f"http://0.0.0.0:{os.getenv('PORT', '5000')}")
})

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger = Swagger(app, config=swagger_config, template={
    "info": {
        "title": "Restaurant Review Sentiment Model API - Team 8",
        "description": "Machine learning model API for analyzing sentiment in restaurant reviews",
        "version": os.getenv('VERSION', '1'),
    }
})

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
    
class HFModel:
    def __init__(self, version="1"):
        # Download model and metadata from HF Hub
        model_path = hf_hub_download(
            repo_id="todor-cmd/sentiment-classifier",
            filename="sentiment_classifier.joblib",
            revision=version
        )
        
        metadata_path = hf_hub_download(
            repo_id="todor-cmd/sentiment-classifier", 
            filename="metadata.json",
            revision=version
        )

        # Load model and metadata
        classifier = joblib.load(model_path)
        with open(metadata_path) as f:
            metadata = json.load(f)
            
        self.classifier = classifier
        self.metadata = metadata
        logger.info(f"Loaded model from {model_path} and metadata from {metadata_path}")
        logger.info("Initialized HFModel")
    
    def predict(self, features):
        """Predict sentiment using the classifier"""
        logger.info(f"Predicting with features: {features}")
        return self.classifier.predict(features)
    
    def predict_proba(self, features):
        """Predict probabilities using the classifier"""
        logger.info(f"Predicting probabilities with features: {features}")
        return self.classifier.predict_proba(features)


class SentimentService:
    def __init__(self):
        """Initialize with real preprocessor and hugging face model"""
        self.model = HFModel()
        self.preprocessor = Preprocessor(vectorizer_path='/app/c1_BoW_Sentiment_Model.pkl')
        logger.info("Initialized with HF model and lib-ml preprocessor")

# Initialize service
service = SentimentService()

@app.route("/health", methods=["GET"])
def health_check():
    """
    Service health endpoint
    ---
    tags:
      - System
    responses:
      200:
        description: Service health information
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            service:
              type: string
            environment:
              type: string
            endpoint:
              type: string
    """
    return jsonify({
        "status": "healthy",
        "service": "restaurant-sentiment",
        "environment": app.config['ENV'],
        "endpoint": app.config['MODEL_SERVICE_ENDPOINT']
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict restaurant review sentiment.
    ---
    consumes:
        - application/json
    parameters:
        - name: input_data
          in: formData
          description: JSON object containing review to be classified
          required: true
        - name: x-user-id
          in: header
          type: string
          description: User ID for session consistency
    responses:
        200:
            description: "The result of the classification"
            schema:
                type: object
                properties:
                    sentiment:
                        type: string
                    confidence:
                        type: number
                    processed_review:
                        type: string
                    endpoint:
                        type: string
                    warning:
                        type: string
        400:
            description: "Invalid input"
    """
    try:
        user_id = request.headers.get('x-user-id', 'unknown')
        logger.debug(f"Received request with x-user-id: {user_id}")
        
        input_data = request.get_json()
        if not input_data or 'review' not in input_data:
            return jsonify({"error": "Missing 'review' field in request body"}), 400

        review = input_data['review']
        logger.info(f"Received review: {review}")
        
        processed_review = service.preprocessor.preprocess(review)
        logger.info(f"Processed review: {processed_review}")

        features = [service.preprocessor.vectorize_single(processed_review)]
        logger.debug(f"Vectorized features: {features}")

        prediction = service.model.predict(features)[0]
        confidence = service.model.predict_proba(features)[0][1]
        logger.info(f"Prediction: {prediction}, Confidence: {confidence}")

        return jsonify({
            "sentiment": "positive" if prediction == 1 else "negative",
            "confidence": float(confidence),
            "processed_review": processed_review,
            "endpoint": app.config['MODEL_SERVICE_ENDPOINT']
        })

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": "Prediction failed"}), 500

@app.route('/dumbpredict', methods=['POST'])
def dumbpredict():
    """
    Simple mock prediction endpoint for testing
    ---
    consumes:
        - application/json
    parameters:
        - name: input_data
          in: formData
          description: JSON object containing review to be classified
          required: true
    responses:
        200:
            description: "Simple mock response"
            schema:
                type: object
                properties:
                    result:
                        type: string
                    classifier:
                        type: string
                    review:
                        type: string
                    note:
                        type: string
    """
    input_data = request.get_json()
    review = input_data.get('review', '') if input_data else ''

    return jsonify({
        "result": "Positive",
        "classifier": "decision tree",
        "review": review[:500],  # Truncate for safety
        "note": "Simple mock response from dumbpredict endpoint"
    })

if __name__ == '__main__':
    logger.info(f"Starting service in {app.config['ENV']} mode on {app.config['HOST']}:{app.config['PORT']}")
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )