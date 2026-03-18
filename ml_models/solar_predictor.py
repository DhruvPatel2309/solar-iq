import numpy as np
import os
import pickle
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "solar_model.pkl")

LOCATION_IRRADIANCE = {
    "mumbai": 5.5, "delhi": 5.8, "bangalore": 5.6, "chennai": 5.7,
    "hyderabad": 5.6, "kolkata": 4.9, "ahmedabad": 6.0, "pune": 5.5,
    "jaipur": 6.2, "lucknow": 5.4, "surat": 5.8, "bhopal": 5.6,
    "default": 5.0
}

def get_irradiance(location: str) -> float:
    loc = location.strip().lower()
    for city, val in LOCATION_IRRADIANCE.items():
        if city in loc:
            return val
    return LOCATION_IRRADIANCE["default"]

def get_season_factor(date_str: str) -> float:
    try:
        month = datetime.strptime(date_str, "%Y-%m-%d").month
    except:
        month = datetime.now().month
    factors = {1:0.85,2:0.90,3:1.00,4:1.10,5:1.15,6:0.85,7:0.80,8:0.85,9:0.95,10:1.05,11:0.95,12:0.85}
    return factors.get(month, 1.0)

def build_model():
    from sklearn.ensemble import RandomForestRegressor
    np.random.seed(42)
    n = 2000
    irradiance  = np.random.uniform(3.5, 7.0, n)
    panel_area  = np.random.uniform(5, 500, n)
    efficiency  = np.random.uniform(0.10, 0.22, n)
    season      = np.random.uniform(0.70, 1.20, n)
    temp_loss   = np.random.uniform(0.85, 0.97, n)
    noise       = np.random.normal(0, 0.05, n)
    kwh = irradiance * panel_area * efficiency * season * temp_loss * (1 + noise)
    kwh = np.clip(kwh, 0, None)
    X = np.column_stack([irradiance, panel_area, efficiency, season, temp_loss])
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, kwh)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return model

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return build_model()

def predict_solar_output(location, panel_area, panel_efficiency, target_date):
    irradiance    = get_irradiance(location)
    season_factor = get_season_factor(target_date)
    temp_loss     = 0.92
    try:
        model = load_model()
        X = np.array([[irradiance, panel_area, panel_efficiency/100, season_factor, temp_loss]])
        predicted_kwh = float(model.predict(X)[0])
    except:
        predicted_kwh = irradiance * panel_area * (panel_efficiency/100) * season_factor * temp_loss

    predicted_kwh = round(max(predicted_kwh, 0), 2)
    daily_kwh     = predicted_kwh
    monthly_kwh   = round(daily_kwh * 30, 2)
    yearly_kwh    = round(daily_kwh * 365, 2)
    co2_saved_kg  = round(yearly_kwh * 0.82, 1)
    money_saved   = round(yearly_kwh * 8, 0)

    return {
        "location": location, "panel_area": panel_area, "panel_efficiency": panel_efficiency,
        "irradiance": irradiance, "season_factor": season_factor,
        "predicted_kwh": daily_kwh, "monthly_kwh": monthly_kwh,
        "yearly_kwh": yearly_kwh, "co2_saved_kg": co2_saved_kg,
        "money_saved_inr": money_saved, "target_date": target_date,
        "model": "RandomForest ML"
    }
