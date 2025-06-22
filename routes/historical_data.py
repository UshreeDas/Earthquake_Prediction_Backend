from bson.decimal128 import Decimal128
from fastapi import APIRouter
from pymongo.collection import Collection
from models.historical_data import EarthquakeData

router = APIRouter()

def init_routes(collection: Collection):
    @router.get("/historical-data")
    def get_historical_data():
        data = list(collection.find({}, {"_id": 0}))
        
        # Convert Decimal128 to float manually
        def convert_decimal(obj):
            for k, v in obj.items():
                if isinstance(v, Decimal128):
                    obj[k] = float(v.to_decimal())
            return obj

        return {"data": [convert_decimal(doc) for doc in data]}

    @router.post("/add-record")
    def add_record(record: EarthquakeData):
        collection.insert_one(record.dict())
        return {"message": "Record inserted"}
