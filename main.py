from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from routes import historical_data, fault_line  

app = FastAPI()

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

# Initialize and register routes
historical_data.init_routes(collection)
fault_line.init_fault_line_routes(fault_line_collection)  

app.include_router(historical_data.router)
app.include_router(fault_line.router)
