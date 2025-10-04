from pydantic import BaseModel
from typing import Optional, List, Literal
import datetime

# ========== Face Recognition Schemas ==========


class RegisterFaceReq(BaseModel):
    warehouse_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    image_base64: str


class RegisterFaceRes(BaseModel):
    status: Literal["ok"]
    employee_id: int
    employee_name: str


class CheckReq(BaseModel):
    image_base64: str
    warehouse_id: Optional[int] = None


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


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class Company(BaseModel):
    id: int
    name: str
    username: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ========== Role Schemas ==========


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Role(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ========== User Schemas ==========


class UserCreate(BaseModel):
    company_id: int
    role_id: int
    username: str
    password: str
    email: Optional[str] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    role_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class User(BaseModel):
    id: int
    company_id: int
    role_id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ========== Warehouse Schemas ==========


class WarehouseCreate(BaseModel):
    company_id: int
    name: str
    location: Optional[str] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class Warehouse(BaseModel):
    id: int
    company_id: int
    name: str
    location: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ========== Tablet Schemas ==========


class TabletCreate(BaseModel):
    warehouse_id: int
    name: str


class TabletUpdate(BaseModel):
    name: Optional[str] = None
    warehouse_id: Optional[int] = None
    jwt_token: Optional[str] = None


class Tablet(BaseModel):
    id: int
    warehouse_id: int
    name: str
    last_sync: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ========== Employee Schemas ==========


class EmployeeCreate(BaseModel):
    warehouse_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    warehouse_id: Optional[int] = None


class Employee(BaseModel):
    id: int
    warehouse_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


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
        from_attributes = True


class UserLoginLog(BaseModel):
    id: int
    user_id: int
    timestamp: datetime.datetime
    location: Optional[str] = None
    browser: Optional[str] = None

    class Config:
        from_attributes = True


class AccessLog(BaseModel):
    id: int
    employee_id: int
    warehouse_id: Optional[int] = None
    event: str
    ts: datetime.datetime

    class Config:
        from_attributes = True


# ========== Report Schemas ==========


class EmployeeCheckInReport(BaseModel):
    employee_id: int
    employee_name: str
    total_check_ins: int
    total_check_outs: int
    last_event: str
    last_event_time: datetime.datetime


class WarehouseActivityReport(BaseModel):
    warehouse_id: int
    warehouse_name: str
    total_events: int
    unique_employees: int
