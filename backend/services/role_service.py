from sqlalchemy.orm import Session
from typing import List, Optional
from models import Role


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()
