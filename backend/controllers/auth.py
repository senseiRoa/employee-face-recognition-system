from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

from services import auth_service
from database import get_db
from dependencies import get_current_user
from models import User
from utils.password_policy import PasswordValidator, PasswordValidationError

router = APIRouter()


# Request schemas
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    warehouse_id: Optional[int] = None
    role_id: Optional[int] = 3  # Default role 'employee'
    record_timezone: Optional[str] = "UTC"  # NEW: Timezone when user is created

    @validator("password")
    def validate_password(cls, v, values):
        """Validate that password complies with security policies"""
        try:
            username = values.get("username")
            email = values.get("email")
            PasswordValidator.validate_password(v, username, email)
        except PasswordValidationError as e:
            raise ValueError(f"Password validation failed: {e.message}")
        return v


class LoginRequest(BaseModel):
    username_or_email: str
    password: str
    client_timezone: Optional[str] = "UTC"  # NEW: Client timezone for login tracking


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/setup-admin", status_code=status.HTTP_201_CREATED)
def setup_first_admin(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Special endpoint to create the first system administrator
    Only works if there are no admin users in the system
    """
    from services.user_service import get_users
    from services.role_service import get_role_by_name

    # Verify if at least one admin already exists
    admin_role = get_role_by_name(db, "admin")
    if admin_role:
        existing_admins = get_users(db, skip=0, limit=1)
        admin_users = [
            user for user in existing_admins if user.role_id == admin_role.id
        ]

        if admin_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System already has admin users. Use /auth/register with proper authentication.",
            )

    try:
        # Forzar role admin y company 1 para el setup inicial
        result = auth_service.register_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            warehouse_id=1,  # Default demo warehouse
            role_id=1,  # Admin role
        )
        return {
            **result,
            "message": "First admin user created successfully. Use /auth/register for subsequent users.",
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin user: {str(e)}",
        )


@router.post("/login", response_model=LoginResponse)
def login_for_access_token(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and get access token
    """
    try:
        result = auth_service.login(
            db=db,
            username_or_email=login_data.username_or_email,
            password=login_data.password,
            client_timezone=login_data.client_timezone,  # NEW: Pass client timezone
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}",
        )


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.name,
        "warehouse_id": current_user.warehouse_id,
        "warehouse_name": current_user.warehouse.name,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
    }
