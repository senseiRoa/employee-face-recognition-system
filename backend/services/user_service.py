from sqlalchemy.orm import Session
from typing import List, Optional
from models import User
from utils.security import get_password_hash as hash_password
import datetime


class UserService:
    """
    Servicio para gestión de usuarios con soporte completo de seguridad
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        warehouse_id: int = 1,
        role_id: int = 3,
        record_timezone: str = "UTC",  # NEW: Add timezone parameter
    ) -> User:
        """
        Create a new user with timezone tracking
        """
        hashed_password = hash_password(password)

        db_user = User(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            warehouse_id=warehouse_id,
            role_id=role_id,
            is_active=True,
            created_at=datetime.datetime.utcnow(),
            password_changed_at=datetime.datetime.utcnow(),
            record_timezone=record_timezone,  # NEW: Store timezone when user was created
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_reset_token(self, reset_token: str) -> Optional[User]:
        """
        Get user by reset token
        """
        return (
            self.db.query(User)
            .filter(
                User.reset_token == reset_token,
                User.reset_token_expires > datetime.datetime.utcnow(),
            )
            .first()
        )

    def get_users(
        self, warehouse_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get list of users with optional filters
        """
        query = self.db.query(User)
        if warehouse_id:
            query = query.filter(User.warehouse_id == warehouse_id)
        return query.offset(skip).limit(limit).all()

    def update_user(
        self,
        user_id: int,
        username: str = None,
        email: str = None,
        password: str = None,
        first_name: str = None,
        last_name: str = None,
        warehouse_id: int = None,
        role_id: int = None,
        is_active: bool = None,
    ) -> Optional[User]:
        """
        Update an existing user
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        if username is not None:
            db_user.username = username
        if email is not None:
            db_user.email = email
        if password is not None:
            db_user.password = hash_password(password)
            db_user.password_changed_at = datetime.datetime.utcnow()
        if first_name is not None:
            db_user.first_name = first_name
        if last_name is not None:
            db_user.last_name = last_name
        if warehouse_id is not None:
            db_user.warehouse_id = warehouse_id
        if role_id is not None:
            db_user.role_id = role_id
        if is_active is not None:
            db_user.is_active = is_active

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Update the last login timestamp
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        db_user.last_login = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True


# Mantener compatibilidad con funciones originales
def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
    warehouse_id: int = 1,
    role_id: int = 3,
) -> User:
    service = UserService(db)
    return service.create_user(
        username, email, password, first_name, last_name, warehouse_id, role_id
    )


def get_user(db: Session, user_id: int) -> Optional[User]:
    service = UserService(db)
    return service.get_user_by_id(user_id)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    service = UserService(db)
    return service.get_user_by_username(username)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    service = UserService(db)
    return service.get_user_by_email(email)


def get_users(
    db: Session, warehouse_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[User]:
    service = UserService(db)
    return service.get_users(warehouse_id, skip, limit)


def update_user(
    db: Session,
    user_id: int,
    username: str = None,
    email: str = None,
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    warehouse_id: int = None,
    role_id: int = None,
    is_active: bool = None,
) -> Optional[User]:
    service = UserService(db)
    return service.update_user(
        user_id,
        username,
        email,
        password,
        first_name,
        last_name,
        warehouse_id,
        role_id,
        is_active,
    )


def update_last_login(db: Session, user_id: int) -> Optional[User]:
    service = UserService(db)
    return service.update_last_login(user_id)


def delete_user(db: Session, user_id: int) -> bool:
    service = UserService(db)
    return service.delete_user(user_id)
