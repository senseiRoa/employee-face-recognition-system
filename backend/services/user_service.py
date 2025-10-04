from sqlalchemy.orm import Session
from typing import List, Optional
from models import User
from schemas import UserCreate, UserUpdate
from utils.security import get_password_hash


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data['password'] = hashed_password
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[User]:
    query = db.query(User)
    if company_id:
        query = query.filter(User.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if 'password' in update_data and update_data['password']:
        update_data['password'] = get_password_hash(update_data['password'])
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True
