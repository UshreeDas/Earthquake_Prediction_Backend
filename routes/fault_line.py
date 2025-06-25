from fastapi import APIRouter
from pymongo.collection import Collection
from bson import ObjectId, Decimal128

router = APIRouter()

def convert_mongo_types(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, Decimal128):
            doc[key] = float(value.to_decimal())
        elif isinstance(value, dict):
            doc[key] = convert_mongo_types(value)
        elif isinstance(value, list):
            doc[key] = [convert_mongo_types(item) if isinstance(item, dict) else item for item in value]
    return doc

def init_fault_line_routes(collection: Collection):
    @router.get("/fault-lines")
    def get_fault_lines():
        raw_data = list(collection.find({}))
        clean_data = [convert_mongo_types(doc) for doc in raw_data]
        return {"data": clean_data}
