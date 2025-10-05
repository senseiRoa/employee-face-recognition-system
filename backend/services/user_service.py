from sqlalchemy.orm import Session
from typing import List, Optional
from models import User
from utils.password import hash_password
import datetime


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
    company_id: int = 1,
    role_id: int = 3,
) -> User:
    """
    Create a new user
    """
    hashed_password = hash_password(password)

    db_user = User(
        username=username,
        email=email,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        company_id=company_id,
        role_id=role_id,
        is_active=True,
        created_at=datetime.datetime.utcnow(),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Get user by ID
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get user by username
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email
    """
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[User]:
    """
    Get list of users with optional filters
    """
    query = db.query(User)
    if company_id:
        query = query.filter(User.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def update_user(
    db: Session,
    user_id: int,
    username: str = None,
    email: str = None,
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    is_active: bool = None,
) -> Optional[User]:
    """
    Update an existing user
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    if username is not None:
        db_user.username = username
    if email is not None:
        db_user.email = email
    if password is not None:
        db_user.password = hash_password(password)
    if first_name is not None:
        db_user.first_name = first_name
    if last_name is not None:
        db_user.last_name = last_name
    if is_active is not None:
        db_user.is_active = is_active

    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_login(db: Session, user_id: int) -> Optional[User]:
    """
    Update the last login timestamp
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.last_login = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True
