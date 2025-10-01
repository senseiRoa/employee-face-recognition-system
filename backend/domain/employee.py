from typing import List
from pydantic import BaseModel

class Employee(BaseModel):
    id: str
    name: str
    encodings: List[str] = []

    class Config:
        orm_mode = True
