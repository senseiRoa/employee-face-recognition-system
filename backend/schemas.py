from pydantic import BaseModel
from typing import Optional, List, Literal

class RegisterFaceReq(BaseModel):
    employee_id: str
    name: str
    image_base64: str

class RegisterFaceRes(BaseModel):
    status: Literal["ok"]
    employee_id: str

class CheckReq(BaseModel):
    image_base64: str

class CheckRes(BaseModel):
    recognized: bool
    employee_id: Optional[str] = None
    name: Optional[str] = None
    distance: Optional[float] = None
    event: Optional[Literal["in","out"]] = None
    ts: Optional[str] = None
