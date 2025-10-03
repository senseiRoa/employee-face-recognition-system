from sqlalchemy.orm import Session
from models import AccessLog, LoginLog

def get_access_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AccessLog).order_by(AccessLog.ts.desc()).offset(skip).limit(limit).all()

def get_login_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LoginLog).order_by(LoginLog.timestamp.desc()).offset(skip).limit(limit).all()
