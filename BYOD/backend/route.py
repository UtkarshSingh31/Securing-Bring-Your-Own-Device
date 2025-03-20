from flask import Blueprint, request, jsonify
from backend.logging_handler import log_visit
import pickle


# Blueprint for routes
app = Blueprint("app", __name__)

# Load the trained model
model_filename = "svm_stem(3,3).sav"
loaded_model = pickle.load(open(model_filename, "rb"))


CATEGORY_MAP = {
    0: "Education",
    1: "Business/Corporate",
    2: "News",
    3: "Health and Fitness",
    4: "Law and Government",
    5: "Computers and Technology",
    6: "Games",
    7: "Streaming Services",
    8: "Social Networking and Messaging",
    9: "Adult",
    10: "Forums",
    11: "E-Commerce",
    12: "Food",
    13: "Photography",
    14: "Travel",
    15: "Sports"
}

# Endpoint for predicting URL category
@app.route("/predict", methods=["POST"])
def predict():
    """Predicts category of URLs and logs visits"""
    data = request.get_json()
    urls = data.get("urls", [])

    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    url_vectors = vectorizer.transform(urls)
    predictions = loaded_model.predict(url_vectors)

    results = []
    for url, pred in zip(urls, predictions):
        category = CATEGORY_MAP[pred]
        results.append({"url": url, "category": category})
        
        # Log visit with assumed time (example: 120 seconds per visit)
        log_visit(url, category, time_spent=120)

    return jsonify(results)

# Endpoint for fetching logs
@app.route("/logs", methods=["GET"])
def logs():
    """Fetch all logs"""
    try:
        with open("usage_logs.log", "r") as f:
            log_data = f.readlines()
        return jsonify({"logs": log_data})
    except FileNotFoundError:
        return jsonify({"error": "Log file not found"}), 500

# Endpoint for fetching alerts
@app.route("/alerts", methods=["GET"])
def alerts():
    """Fetch all alerts"""
    try:
        with open("usage_logs.log", "r") as f:
            alert_data = [line for line in f if "ALERT" in line]
        return jsonify({"alerts": alert_data})
    except FileNotFoundError:
        return jsonify({"error": "Log file not found"}), 500
