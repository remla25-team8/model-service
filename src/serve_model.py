"""
Flask API for restaurant sentiment detection model-service.
"""

# import joblib
from flask import Flask, jsonify, request
from flasgger import Swagger
from lib_ml.preprocessor import Preprocessor
import logging

app = Flask(__name__)
swagger = Swagger(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockModel:
    """Temporary mock model until real one is ready"""
    def predict(self, features):
        # Simple mock logic - replace with real model later
        return [1 if "good" in str(features).lower() else 0]
    
    def predict_proba(self, features):
        # Mock confidence scores
        pred = self.predict(features)[0]
        return [[1.0, 0.0]] if pred == 0 else [[0.0, 1.0]]

class SentimentService:
    def __init__(self):
        """Initialize with mock components"""
        self.model = MockModel()
        self.preprocessor = Preprocessor(vectorizer_path=None)
        logger.info("Initialized with mock services")

# Initialize service
service = SentimentService()

@app.route("/health", methods=["GET"])
def health_check():
    """Service health endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "restaurant-sentiment-mock",
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
                    example: "The food was delicious!".
    responses:
        200:
            description: "The result of the classification: 'positive' or 'negative'."
    """
    input_data = request.get_json()
    review = input_data.get('review')

    processed_review = service.preprocessor.preprocess(review)

    # Mock prediction (to be replaced)
    features = [[0]]  # Temporary mock features
    prediction = service.model.predict(features)[0]
    confidence = service.model.predict_proba(features)[0][1]

    res = {
        "sentiment": "positive" if prediction == 1 else "negative",
        "confidence": float(confidence),
        "processed_review": processed_review,
        "result": prediction,
        "classifier": "decision tree",
        "review": review
    }
    print(res)
    return jsonify(res)

@app.route('/dumbpredict', methods=['POST'])
def dumbpredict():
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
                    example: "The food was delicious!".
    responses:
        200:
            description: "The result of the classification: 'positive' or 'negative'."
    """
    input_data = request.get_json()
    review = input_data.get('review')

    res = {
        "result": "Positive",
        "classifier": "decision tree",
        "review": review
    }
    print(res)
    return jsonify(res)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)