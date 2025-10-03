from pydantic import BaseModel
from typing import Optional, List, Literal
import datetime

# ========== Face Recognition Schemas ==========

class RegisterFaceReq(BaseModel):
    employee_id: int
    name: str
    image_base64: str

class RegisterFaceRes(BaseModel):
    status: Literal["ok"]
    employee_id: int

class CheckReq(BaseModel):
    image_base64: str

class CheckRes(BaseModel):
    recognized: bool
    employee_id: Optional[int] = None
    name: Optional[str] = None
    distance: Optional[float] = None
    event: Optional[Literal["in", "out"]] = None
    ts: Optional[str] = None

# ========== Company Schemas ==========

class CompanyCreate(BaseModel):
    name: str
    username: str
    password: str

class Company(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        orm_mode = True

# ========== Authentication Schemas ==========

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginReq(BaseModel):
    username: str
    password: str

# ========== Log Schemas ==========

class LoginLog(BaseModel):
    id: int
    company_id: int
    timestamp: datetime.datetime
    location: Optional[str] = None
    browser: Optional[str] = None

    class Config:
        orm_mode = True

class AccessLog(BaseModel):
    id: int
    employee_id: int
    event: str
    ts: datetime.datetime

    class Config:
        orm_mode = True