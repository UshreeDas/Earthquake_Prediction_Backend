from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

# Import routers
from routes import historical_data, fault_line
from routes.lat_long_zone import router as prediction_router
from routes.earthquake_combined import router as combined_router  # ✅ Full prediction router
from routes.predict_mag import router as predict_mag_router
from routes.auth import router as auth_router
from routes.add_data import router as add_data_router

# Import Database funtions
from database.db import database, metadata, engine
from contextlib import asynccontextmanager
from sqlalchemy.orm import declarative_base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await database.connect()
    yield
    # shutdown
    await database.disconnect()

     
app = FastAPI(title="Earthquake Prediction API", lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# MongoDB setup
client = MongoClient("mongodb://DMMPrice:Babai6157201@82.29.161.123:27017/")
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
app.include_router(predict_mag_router, prefix="/predict/mag") 
app.include_router(add_data_router, prefix="/data")         # ➕ /data/add_record

# include auth routers
app.include_router(auth_router, prefix="/auth")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to the Earthquake Prediction API. Visit /docs for Swagger UI."
    }
