from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

router = APIRouter()    

# Pydantic model based on the example data
class EarthquakeRecord(BaseModel):
    time_eq: str
    latitude_eq: float
    longitude_eq: float
    depth_eq: int
    magnitude_eq: float
    depth_error_eq: int
    zone_eq: int
    year_eq: int
    month_eq: int
    day_eq: int
    min_proximity_km: float
    avg_proximity_km: float
    max_proximity_km: float
    fault_count_within_50km: int
    fault_count_within_100km: int
    zone_fault: int
    latitude_fault: float
    longitude_fault: float
    area_fault: str
    state_fault: str
    state_area_fault: int
    slip_rate_mm_per_yr_fault: int
    plate_boundary_type_fault: str
    fault_type_fault: str
    fault_length_km_fault: int
    total_fault_length_fault: int
    rock_type_fault: str
    rock_factor_scaled_fault: float
    soil_type_fault: str
    soil_factor_scaled_fault: float
    fracture_factor_scaled_fault: float
    strain_rate_fault: str  # Scientific notation as string
    seismic_hazard_fault: str
    fault_density_fault: float
    attenuation_factor_fault: float
    AF_Classification_fault: str
    zone_mismatch_flag: str

CSV_FILE_PATH = "models/earthquake_final_dataset_full_2.csv"

def ensure_csv_exists():
    """Create models folder and CSV file if they don't exist"""
    os.makedirs("models", exist_ok=True)

    if not os.path.exists(CSV_FILE_PATH):
        # Create empty CSV with headers
        columns = [
            "time_eq", "latitude_eq", "longitude_eq", "depth_eq", "magnitude_eq",
            "depth_error_eq", "zone_eq", "year_eq", "month_eq", "day_eq",
            "min_proximity_km", "avg_proximity_km", "max_proximity_km",
            "fault_count_within_50km", "fault_count_within_100km", "zone_fault",
            "latitude_fault", "longitude_fault", "area_fault", "state_fault",
            "state_area_fault", "slip_rate_mm_per_yr_fault", "plate_boundary_type_fault",
            "fault_type_fault", "fault_length_km_fault", "total_fault_length_fault",
            "rock_type_fault", "rock_factor_scaled_fault", "soil_type_fault",
            "soil_factor_scaled_fault", "fracture_factor_scaled_fault",
            "strain_rate_fault", "seismic_hazard_fault", "fault_density_fault",
            "attenuation_factor_fault", "AF_Classification_fault", "zone_mismatch_flag"
        ]
        pd.DataFrame(columns=columns).to_csv(CSV_FILE_PATH, index=False)

@router.post("/add_record")
async def add_record(record: EarthquakeRecord):
    """Add a new earthquake record to the dataset"""
    try:
        ensure_csv_exists()
        
        # Convert record to dictionary
        record_dict = record.dict()
        
        # Create DataFrame from the record
        new_record_df = pd.DataFrame([record_dict])
        
        # Append to existing CSV
        new_record_df.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)
        
        return {"message": "Record added successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding record: {str(e)}")

