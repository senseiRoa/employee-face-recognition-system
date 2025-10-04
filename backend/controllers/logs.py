from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from services import log_service
from schemas import AccessLog, LoginLog, UserLoginLog
from dependencies import get_current_user
from models import Company

router = APIRouter()


@router.get("/access", response_model=List[AccessLog])
def list_access_logs(
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return log_service.get_access_logs(
        db,
        employee_id=employee_id,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.get("/login", response_model=List[LoginLog])
def list_login_logs(
    company_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return log_service.get_login_logs(
        db,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.get("/user-login", response_model=List[UserLoginLog])
def list_user_login_logs(
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Company = Depends(get_current_user)
):
    return log_service.get_user_login_logs(
        db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
