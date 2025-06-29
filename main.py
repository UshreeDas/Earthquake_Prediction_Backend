from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

# Import routers
from routes import historical_data, fault_line
from routes.lat_long_zone import router as prediction_router
from routes.earthquake_combined import router as combined_router  # ✅ Full prediction router

app = FastAPI(title="Earthquake Prediction API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["earthquake"]
collection = db["historical_data"]
fault_line_collection = db["fault_line"]

# Register Mongo-based routers
historical_data.init_routes(collection)
fault_line.init_fault_line_routes(fault_line_collection)

# Include routers
app.include_router(historical_data.router)
app.include_router(fault_line.router)
app.include_router(prediction_router, prefix="/api")       # ➕ /api/predict (lat/lon/zone)
app.include_router(combined_router, prefix="/api")         # ➕ /api/predict-full (lat/lon/zone + magnitude)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to the Earthquake Prediction API. Visit /docs for Swagger UI."
    }
