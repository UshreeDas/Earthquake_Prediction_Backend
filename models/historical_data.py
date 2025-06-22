# models/historical_data.py

from pydantic import BaseModel
from typing import Optional

class EarthquakeData(BaseModel):
    time_eq: str
    latitude_eq: float
    longitude_eq: float
    depth_eq: float
    magnitude_eq: float
    depth_error_eq: float
    zone_eq: int
    year_eq: int
    month_eq: int
    day_eq: int

    min_proximity_km: Optional[float]
    avg_proximity_km: Optional[float]
    max_proximity_km: Optional[float]
    fault_count_within_50km: Optional[int]
    fault_count_within_100km: Optional[int]
    
    zone_fault: Optional[int]
    latitude_fault: Optional[float]
    longitude_fault: Optional[float]
    area_fault: Optional[str]
    state_fault: Optional[str]
    state_area_fault: Optional[int]
    
    slip_rate_mm_per_yr_fault: Optional[int]
    plate_boundary_type_fault: Optional[str]
    fault_type_fault: Optional[str]
    fault_length_km_fault: Optional[int]
    total_fault_length_fault: Optional[int]
    rock_type_fault: Optional[str]
    rock_factor_scaled_fault: Optional[float]
    soil_type_fault: Optional[str]
    soil_factor_scaled_fault: Optional[float]
    fracture_factor_scaled_fault: Optional[float]
    strain_rate_fault: Optional[float]
    seismic_hazard_fault: Optional[str]
    fault_density_fault: Optional[float]
    attenuation_factor_fault: Optional[float]
    AF_classification_fault: Optional[str]
    zone_mismatch_flag: Optional[str]
