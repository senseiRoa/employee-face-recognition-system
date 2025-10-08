from sqlalchemy.orm import Session
from typing import Optional
from models import AccessLog, UserLoginLog
from datetime import datetime


def get_access_logs(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(AccessLog)

    if employee_id:
        query = query.filter(AccessLog.employee_id == employee_id)
    if warehouse_id:
        query = query.filter(AccessLog.warehouse_id == warehouse_id)
    if start_date:
        query = query.filter(AccessLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AccessLog.timestamp <= end_date)

    return query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()


def get_user_login_logs(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(UserLoginLog)

    if user_id:
        query = query.filter(UserLoginLog.user_id == user_id)
    if start_date:
        query = query.filter(UserLoginLog.timestamp >= start_date)
    if end_date:
        query = query.filter(UserLoginLog.timestamp <= end_date)

    return query.order_by(UserLoginLog.timestamp.desc()).offset(skip).limit(limit).all()


def create_user_login_log(
    db: Session, user_id: int, location: str = None, browser: str = None
):
    log = UserLoginLog(user_id=user_id, location=location, browser=browser)
    db.add(log)
    db.commit()
    return log
