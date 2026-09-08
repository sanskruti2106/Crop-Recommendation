from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = Flask(__name__)

# ---------------- 1. DATASET & ML MODEL INITIALIZATION ----------------

# Load crop dataset
df = pd.read_csv("Crop_recommendation.csv")

# Input features and target
X = df.drop("label", axis=1)
y = df["label"]

# Train-Test Split (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Train Random Forest Classifier
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)

# Calculate Accuracy
y_pred = model.predict(X_test)
model_accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)

# Compute per-crop baseline statistics for radar chart and catalog
crop_catalog = {}
for label_name, group in df.groupby("label"):
    crop_catalog[label_name] = {}
    for col in ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]:
        crop_catalog[label_name][col] = {
            "mean": round(float(group[col].mean()), 1),
            "min": round(float(group[col].min()), 1),
            "max": round(float(group[col].max()), 1)
        }

# Feature Importance
feature_names = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
feature_importances = dict(zip(feature_names, [round(val * 100, 2) for val in model.feature_importances_]))


# ---------------- 2. FLASK ROUTES & REST ENDPOINTS ----------------

@app.route("/", methods=["GET", "POST"])
def home():
    crop = None
    confidence = None
    top_probabilities = []
    user_input = {}
    crop_stats = {}

    if request.method == "POST":
        try:
            N = float(request.form["N"])
            P = float(request.form["P"])
            K = float(request.form["K"])
            temperature = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])

            user_input = {
                "N": N, "P": P, "K": K,
                "temperature": temperature, "humidity": humidity,
                "ph": ph, "rainfall": rainfall
            }
            user_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], columns=feature_names)
            
            # Predict top crop and probabilities
            probs = model.predict_proba(user_data)[0]
            classes = model.classes_
            
            prob_list = []
            for idx, c in enumerate(classes):
                prob_list.append({
                    "crop": c,
                    "probability": round(float(probs[idx]) * 100, 1)
                })
            
            prob_list.sort(key=lambda x: x["probability"], reverse=True)
            
            crop = prob_list[0]["crop"]
            confidence = prob_list[0]["probability"]
            top_probabilities = prob_list
            crop_stats = crop_catalog.get(crop, {})

        except (ValueError, KeyError) as e:
            pass

    return render_template(
        "index.html",
        crop=crop,
        confidence=confidence,
        top_probabilities=top_probabilities,
        user_input=user_input,
        crop_stats=crop_stats,
        accuracy=model_accuracy,
        active_page="home"
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """REST API endpoint for AJAX async prediction & radar data"""
    try:
        data = request.get_json()
        
        N = float(data["N"])
        P = float(data["P"])
        K = float(data["K"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        ph = float(data["ph"])
        rainfall = float(data["rainfall"])

        user_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], columns=feature_names)
        
        probs = model.predict_proba(user_data)[0]
        classes = model.classes_
        
        prob_list = []
        for idx, c in enumerate(classes):
            prob_list.append({
                "crop": c,
                "probability": round(float(probs[idx]) * 100, 1)
            })
        
        prob_list.sort(key=lambda x: x["probability"], reverse=True)
        top_crop = prob_list[0]["crop"]
        confidence = prob_list[0]["probability"]

        # Fetch ideal stats for the predicted crop
        stats = crop_catalog.get(top_crop, {})

        return jsonify({
            "status": "success",
            "top_crop": top_crop,
            "confidence": confidence,
            "probabilities": prob_list[:5],
            "crop_stats": stats
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route("/catalog")
def catalog():
    return render_template(
        "catalog.html",
        crop_catalog=crop_catalog,
        accuracy=model_accuracy,
        active_page="catalog"
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        accuracy=model_accuracy,
        feature_importances=feature_importances,
        active_page="about"
    )


@app.route("/how-it-works")
def how_it_works():
    return render_template(
        "how_it_works.html",
        accuracy=model_accuracy,
        active_page="how_it_works"
    )


@app.route("/api/model-info")
def model_info():
    return jsonify({
        "accuracy": model_accuracy,
        "total_samples": len(df),
        "crop_count": len(crop_catalog),
        "feature_importances": feature_importances
    })


if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    print(f"Starting Crop Recommendation Web Server on http://127.0.0.1:{port}...")
    app.run(host="127.0.0.1", port=port, debug=True)