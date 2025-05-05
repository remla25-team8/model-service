"""
Production-ready Flask API with integrated preprocessing and mock model
"""

from flask import Flask, jsonify, request
from flasgger import Swagger
from lib_ml.preprocessor import Preprocessor
import logging
import os

# Load environment variables first

app = Flask(__name__)

# Configure from environment with defaults
app.config.update({
    'ENV': os.getenv('FLASK_ENV', 'production'),
    'DEBUG': os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
    'HOST': os.getenv('HOST', '0.0.0.0'),
    'PORT': int(os.getenv('PORT', '8080')),
    'MODEL_SERVICE_ENDPOINT': os.getenv('MODEL_SERVICE_ENDPOINT', f"http://0.0.0.0:{os.getenv('PORT', '8080')}")
})

# Configure Swagger
swagger = Swagger(app, template={
    'info': {
        'title': 'Restaurant Sentiment API',
        'description': 'API for predicting sentiment from restaurant reviews',
    }
})

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockModel:
    """Mock model that returns deterministic test responses"""
    def __init__(self):
        logger.warning("Using MOCK model")
        self.classes_ = [0, 1]  # Mimic sklearn model structure
    
    def predict(self, features):
        """Positive if 'good' in text, otherwise negative"""
        text = str(features)
        return [1 if "good" in text.lower() else 0]
    
    def predict_proba(self, features):
        """Mock confidence scores"""
        pred = self.predict(features)[0]
        return [[0.9, 0.1]] if pred == 0 else [[0.1, 0.9]]

class SentimentService:
    def __init__(self):
        """Initialize with real preprocessor and mock model"""
        self.model = MockModel()
        self.preprocessor = Preprocessor(vectorizer_path=None)
        logger.info("Initialized with mock model and real preprocessor")

# Initialize service
service = SentimentService()

@app.route("/health", methods=["GET"])
def health_check():
    """Service health endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "restaurant-sentiment",
        "environment": app.config['ENV'],
        "endpoint": app.config['MODEL_SERVICE_ENDPOINT'],
        "warning": "Using mock model implementation"
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
          in: body
          description: review to be classified.
          required: True
          schema:
            type: object
            required: review
            properties:
                review:
                    type: string
                    example: "The food was delicious!"
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
        input_data = request.get_json()
        if not input_data or 'review' not in input_data:
            return jsonify({"error": "Missing 'review' in request body"}), 400

        review = input_data['review']
        processed_review = service.preprocessor.preprocess(review)
        
        # Mock feature transformation and prediction
        features = [[0]]  # Using placeholder features since we're mocking
        prediction = service.model.predict(features)[0]
        confidence = service.model.predict_proba(features)[0][1]

        return jsonify({
            "sentiment": "positive" if prediction == 1 else "negative",
            "confidence": float(confidence),
            "processed_review": processed_review,
            "endpoint": app.config['MODEL_SERVICE_ENDPOINT'],
            "warning": "mock-response"
        })

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"error": "Prediction service unavailable"}), 500

@app.route('/dumbpredict', methods=['POST'])
def dumbpredict():
    """
    Simple mock prediction endpoint for testing
    ---
    consumes:
        - application/json
    parameters:
        - name: input_data
          in: body
          description: review to be classified.
          required: True
          schema:
            type: object
            required: review
            properties:
                review:
                    type: string
                    example: "The food was delicious!"
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
    review = input_data.get('review', "") if input_data else ""

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