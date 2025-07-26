from flask import Flask, render_template, request
import joblib
import pandas as pd
import numpy as np
from datetime import timedelta

app = Flask(__name__)

# Load your saved model pipeline (with all preprocessing included)
model = joblib.load("delivery_time_model_v1.pkl")

def preprocess_input(form):
    # Parse dates and times
    order_date = pd.to_datetime(form['Order_Date'])  # 'YYYY-MM-DD'
    time_orderd = pd.to_timedelta(form['Time_Orderd'])  # e.g., '13:45:00'
    time_order_picked = pd.to_timedelta(form['Time_Order_picked'])  # e.g., '14:10:00'

    datetime_orderd = order_date + time_orderd
    datetime_picked = order_date + time_order_picked

    # Handle next day pickup
    if datetime_picked < datetime_orderd:
        datetime_picked += timedelta(days=1)

    # Calculate preparation time in minutes
    order_prepare_time = (datetime_picked - datetime_orderd).total_seconds() / 60

    # Extract date/time features
    day = order_date.day
    month = order_date.month
    year = order_date.year
    weekday = order_date.weekday()  # Monday=0, Sunday=6
    is_weekend = int(weekday >= 5)
    is_month_start = int(order_date.is_month_start)
    is_month_end = int(order_date.is_month_end)
    is_quarter_start = int(order_date.is_quarter_start)
    is_quarter_end = int(order_date.is_quarter_end)
    is_year_start = int(order_date.is_year_start)
    is_year_end = int(order_date.is_year_end)
    quarter = order_date.quarter
    day_of_week = weekday
    city_code = 0  # placeholder, adjust if you want to encode City

    # Since lat/lon dropped, distance = 0
    distance = 0.0

    # Compose features dict expected by model
    features = {
        "Delivery_person_Age": int(form['Delivery_person_Age']),
        "Delivery_person_Ratings": float(form['Delivery_person_Ratings']),
        "Weather_conditions": form['Weather_conditions'],
        "Road_traffic_density": form['Road_traffic_density'],
        "Vehicle_condition": int(form['Vehicle_condition']),
        "Type_of_order": form['Type_of_order'],
        "Type_of_vehicle": form['Type_of_vehicle'],
        "multiple_deliveries": form['multiple_deliveries'],
        "Festival": form['Festival'],
        "City": form['City'],
        "day": day,
        "month": month,
        "year": year,
        "weekday": weekday,
        "is_weekend": is_weekend,
        "prep_time_min": order_prepare_time,
        "is_month_start": is_month_start,
        "is_month_end": is_month_end,
        "is_quarter_start": is_quarter_start,
        "is_quarter_end": is_quarter_end,
        "is_year_start": is_year_start,
        "is_year_end": is_year_end,
        "quarter": quarter,
        "day_of_week": day_of_week,
        "City_code": city_code,
        "distance": distance,
        "order_prepare_time": order_prepare_time
    }

    return pd.DataFrame([features])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Preprocess inputs from form
            input_df = preprocess_input(request.form)

            # Predict delivery time
            prediction = model.predict(input_df)[0]
            prediction = round(prediction, 2)

            return render_template("result.html", prediction=prediction)
        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
