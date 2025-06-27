from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from math import isclose

router = APIRouter()

# Load models and dataset
coord_model = joblib.load("models/rf_multioutput_model_lat_lon_zone.pkl")
mag_model = joblib.load("models/rf_magnitude_predictor.pkl")
df5 = pd.read_csv("data/earthquake_final_dataset_full_2.csv")

# Request schema
class EarthquakeInput(BaseModel):
    magnitude_eq: float
    depth_eq: float
    depth_error_eq: float
    min_proximity_km: float
    fault_count_within_50km: int
    slip_rate_mm_per_yr_fault: float
    fault_density_fault: float
    rock_factor_scaled_fault: float
    soil_factor_scaled_fault: float
    strain_rate_fault: float
    attenuation_factor_fault: float
    fault_type_fault: int
    rock_type_fault: int
    soil_type_fault: int
    seismic_hazard_fault: int
    zone_mismatch_flag: int

@router.post("/predict-full")
def predict_full_earthquake(data: EarthquakeInput):
    try:
        # Step 1: Predict coordinates & zone
        test_input_row = pd.DataFrame([data.dict()])
        pred_lat, pred_lon, pred_zone = coord_model.predict(test_input_row)[0]
        pred_zone = int(round(pred_zone))

        # Step 2: Prepare magnitude input
        relevant_features = [
            'depth_eq', 'depth_error_eq', 'fault_density_fault',
            'slip_rate_mm_per_yr_fault', 'strain_rate_fault',
            'attenuation_factor_fault', 'soil_factor_scaled_fault',
            'rock_factor_scaled_fault', 'zone_eq'
        ]
        last_row = df5.dropna(subset=relevant_features).iloc[-1]

        mag_input_row = pd.DataFrame([{
            'depth_eq': last_row['depth_eq'],
            'depth_error_eq': last_row['depth_error_eq'],
            'fault_density_fault': last_row['fault_density_fault'],
            'slip_rate_mm_per_yr_fault': last_row['slip_rate_mm_per_yr_fault'],
            'strain_rate_fault': last_row['strain_rate_fault'],
            'attenuation_factor_fault': last_row['attenuation_factor_fault'],
            'soil_factor_scaled_fault': last_row['soil_factor_scaled_fault'],
            'rock_factor_scaled_fault': last_row['rock_factor_scaled_fault'],
            'zone_eq': pred_zone
        }])

        predicted_magnitude = mag_model.predict(mag_input_row)[0]

        return {
            "predicted_coordinates": {
                "latitude": round(pred_lat, 4),
                "longitude": round(pred_lon, 4)
            },
            "predicted_zone": pred_zone,
            "predicted_magnitude": round(predicted_magnitude, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
