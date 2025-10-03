from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from services import log_service
from schemas import AccessLog, LoginLog
from dependencies import get_current_user
from models import Company

router = APIRouter()

@router.get("/access", response_model=List[AccessLog])
def list_access_logs(db: Session = Depends(get_db), current_user: Company = Depends(get_current_user)):
    return log_service.get_access_logs(db)

@router.get("/login", response_model=List[LoginLog])
def list_login_logs(db: Session = Depends(get_db), current_user: Company = Depends(get_current_user)):
    return log_service.get_login_logs(db)
