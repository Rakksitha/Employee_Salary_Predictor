from flask import Flask, render_template, request
import numpy as np
import joblib
import pandas as pd

app = Flask(__name__)

# Load model, scaler, and columns
model = joblib.load("gbc_model.pkl")
scaler = joblib.load("scaler.pkl")
model_columns = joblib.load("model_columns.pkl")  # List of final columns used during training

education_mapping = {
    "9th": 5,
    "10th": 6,
    "11th": 7,
    "12th": 8,
    "HS-grad": 9,
    "Some-college": 10,
    "Assoc-voc": 11,
    "Assoc-acdm": 12,
    "Bachelors": 13,
    "Masters": 14,
    "Prof-school": 15,
    "Doctorate": 16
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            # Get form data
            age = int(request.form["age"])
            gender = request.form["gender"]
            education_str = request.form["education"]
            education_num = education_mapping.get(education_str, 0)  # default to 0 if not found
            workclass = request.form["workclass"]
            hours = int(request.form["hours"])
            occupation = request.form["occupation"]
            marital = request.form["marital"]
            country = request.form["country"]
            relationship = request.form["relationship"]
            race = request.form["race"]
            gain = int(request.form["gain"])
            loss = int(request.form["loss"])

            # Build raw input dict
            raw_input = {
                "age": age,
                "workclass": workclass,
                "native-country": country,
                "hours-per-week": hours,
                "capital-gain": gain,
                "capital-loss": loss,
                "gender": gender,
                "education-num": education_num,
                "occupation": occupation,
                "marital-status": marital,
                "relationship": relationship,
                "race": race
            }

            # Convert to DataFrame
            input_df = pd.DataFrame([raw_input])

            # One-hot encoding
            input_encoded = pd.get_dummies(input_df)

            # Align with training columns
            input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

            # Scale numerical features (only if your scaler was fit before encoding)
            input_scaled = scaler.transform(input_encoded)

            # Predict
            prediction = model.predict(input_scaled)[0]
            result = ">50K" if prediction == 1 else "<=50K"

            return render_template("predict.html", prediction_text=f"Predicted Income: {result}")

        except Exception as e:
            return render_template("predict.html", prediction_text=f"Error: {str(e)}")
        
    # On GET request, just render form with no result
    return render_template("predict.html")

if __name__ == "__main__":
    app.run(debug=True)
