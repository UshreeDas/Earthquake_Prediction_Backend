from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from math import sqrt
import joblib

router = APIRouter()

# Load model and reference data once (ensure relative paths work correctly)
model = joblib.load("models/rf_multioutput_model_lat_lon_zone.pkl")
df_reference = pd.read_csv("data/earthquake_final_dataset_full_2.csv")
df_fault_reference = df_reference[['latitude_fault', 'longitude_fault', 'area_fault']].copy()

# Input schema
class EarthquakeInput(BaseModel):
    latitude_input: float
    longitude_input: float
    zone_input: int

def format_direction(coord, is_lat=True):
    return f"{abs(coord):.4f}° {'N' if is_lat and coord >= 0 else 'S' if is_lat else 'E' if coord >= 0 else 'W'}"

@router.post("/predict")
def predict_earthquake(data: EarthquakeInput):
    try:
        test_input_row = pd.DataFrame([{
            'magnitude_eq': 4.5,
            'depth_eq': 108.6,
            'depth_error_eq': 10.1,
            'min_proximity_km': 1613.722912,
            'fault_count_within_50km': 0,
            'slip_rate_mm_per_yr_fault': 0.5,
            'fault_density_fault': 0.37,
            'rock_factor_scaled_fault': 0.005,
            'soil_factor_scaled_fault': 0.007,
            'strain_rate_fault': 0.00000000833,
            'attenuation_factor_fault': 0.0057,
            'fault_type_fault': 2,
            'rock_type_fault': 5,
            'soil_type_fault': 5,
            'seismic_hazard_fault': 2,
            'zone_mismatch_flag': 1
        }])

        pred = model.predict(test_input_row)
        pred_lat, pred_lon, pred_zone = pred[0]
        pred_zone = int(round(pred_zone))

        lat_dir = format_direction(pred_lat, True)
        lon_dir = format_direction(pred_lon, False)

        df_fault_reference['distance'] = df_fault_reference.apply(
            lambda row: sqrt((row['latitude_fault'] - pred_lat)**2 + (row['longitude_fault'] - pred_lon)**2),
            axis=1
        )
        nearest_fault_area = df_fault_reference.loc[
            df_fault_reference['distance'].idxmin(), 'area_fault'
        ]

        return {
            "predicted_coordinates": {
                "latitude": lat_dir,
                "longitude": lon_dir
            },
            "predicted_zone": pred_zone,
            "nearest_fault_area": nearest_fault_area
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
