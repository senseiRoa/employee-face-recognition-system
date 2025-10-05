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
    warehouse_id: Optional[int] = 1
    role_id: Optional[int] = 3  # Default role 'employee'

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


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registrar un nuevo usuario (solo para admins y managers)
    """
    # Verificar permisos - solo admin y manager pueden crear usuarios
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create users. Only admins and managers can register new users.",
        )

    # If not admin, can only create users in their own warehouse
    target_warehouse_id = user_data.warehouse_id or current_user.warehouse_id
    if (
        current_user.role.name != "admin"
        and target_warehouse_id != current_user.warehouse_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only create users in their own warehouse",
        )

    # Verify that role_id is valid according to current user permissions
    if current_user.role.name == "manager" and user_data.role_id == 1:  # admin role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers cannot create admin users",
        )

    try:
        result = auth_service.register_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            warehouse_id=target_warehouse_id,
            role_id=user_data.role_id,
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.post("/setup-admin", status_code=status.HTTP_201_CREATED)
def setup_first_admin(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Endpoint especial para crear el primer administrador del sistema
    Solo funciona si no existen usuarios admin en el sistema
    """
    from services.user_service import get_users
    from services.role_service import get_role_by_name

    # Verificar si ya existe al menos un admin
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
    Autenticar usuario y obtener token de acceso
    """
    try:
        result = auth_service.login(
            db=db,
            username_or_email=login_data.username_or_email,
            password=login_data.password,
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
    Obtener información del usuario actual
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
