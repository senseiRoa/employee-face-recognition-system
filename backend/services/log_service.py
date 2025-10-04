from sqlalchemy.orm import Session
from typing import Optional
from models import AccessLog, LoginLog, UserLoginLog
from datetime import datetime


def get_access_logs(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(AccessLog)
    
    if employee_id:
        query = query.filter(AccessLog.employee_id == employee_id)
    if warehouse_id:
        query = query.filter(AccessLog.warehouse_id == warehouse_id)
    if start_date:
        query = query.filter(AccessLog.ts >= start_date)
    if end_date:
        query = query.filter(AccessLog.ts <= end_date)
    
    return query.order_by(AccessLog.ts.desc()).offset(skip).limit(limit).all()


def get_login_logs(
    db: Session,
    company_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(LoginLog)
    
    if company_id:
        query = query.filter(LoginLog.company_id == company_id)
    if start_date:
        query = query.filter(LoginLog.timestamp >= start_date)
    if end_date:
        query = query.filter(LoginLog.timestamp <= end_date)
    
    return query.order_by(LoginLog.timestamp.desc()).offset(skip).limit(limit).all()


def get_user_login_logs(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(UserLoginLog)
    
    if user_id:
        query = query.filter(UserLoginLog.user_id == user_id)
    if start_date:
        query = query.filter(UserLoginLog.timestamp >= start_date)
    if end_date:
        query = query.filter(UserLoginLog.timestamp <= end_date)
    
    return query.order_by(UserLoginLog.timestamp.desc()).offset(skip).limit(limit).all()


def create_login_log(db: Session, company_id: int, location: str = None, browser: str = None):
    log = LoginLog(company_id=company_id, location=location, browser=browser)
    db.add(log)
    db.commit()
    return log


def create_user_login_log(db: Session, user_id: int, location: str = None, browser: str = None):
    log = UserLoginLog(user_id=user_id, location=location, browser=browser)
    db.add(log)
    db.commit()
    return log
