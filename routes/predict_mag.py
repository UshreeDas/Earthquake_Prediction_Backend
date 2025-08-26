from fastapi import APIRouter
from pydantic import BaseModel
from pipelines.mag_predict_pipeline import predict_earthquake

router = APIRouter()

class EarthquakeInput(BaseModel):
    latitude: float
    longitude: float
    zone: int

@router.post("/predict")
def predict_eq(data: EarthquakeInput) -> dict:
    result = predict_earthquake(data.latitude, data.longitude, data.zone)
    print(result)
    return {"prediction": result}