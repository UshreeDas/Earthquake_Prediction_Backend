# models/fault_line.py

from pydantic import BaseModel

class FaultLine(BaseModel):
    Fault_Name: str
    Start_Lat: float
    Start_Lon: float
    End_Lat: float
    End_Lon: float
