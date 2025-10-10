from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.user_service import get_user_by_username, get_user_by_email, get_user
from services.log_service import create_user_login_log  # NEW: Import login logging
from utils.security import verify_password
from utils.jwt_handler import create_access_token
from utils.refresh_tokens import RefreshTokenService


def login(
    db: Session,
    username_or_email: str,
    password: str,
    client_timezone: str = "UTC",
    device_info: str = None,
) -> dict:
    """
    Authenticate user by username or email with timezone tracking
    """
    # Intentar por username primero
    user = get_user_by_username(db, username_or_email)

    # Si no se encuentra por username, intentar por email
    if not user:
        user = get_user_by_email(db, username_or_email)

    # Verify if user exists and password is correct
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    # Update user's last_login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Log successful login with timezone information
    create_user_login_log(
        db=db,
        user_id=user.id,
        location=None,  # Can be extracted from request headers if needed
        browser=None,  # Can be extracted from user agent if needed
        client_timezone=client_timezone,  # NEW: Store client timezone
    )

    # Create access token with user information
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "warehouse_id": user.warehouse_id,
            "role": user.role.name,
            "role_id": user.role.id,
        }
    )

    # Create refresh token
    refresh_token_obj = RefreshTokenService.create_refresh_token(
        db=db, user_id=user.id, device_info=device_info
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_obj.token,
        "token_type": "bearer",
        "expires_in": 15 * 60,  # 15 minutes in seconds
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name,
            "role_id": user.role.id,
            "warehouse_id": user.warehouse_id,
            "warehouse_name": user.warehouse.name,
        },
    }


def refresh_token(db: Session, refresh_token: str) -> dict:
    """
    Get new access token using refresh token
    """
    # Validate and get user from refresh token
    token_obj = RefreshTokenService.validate_refresh_token(db, refresh_token)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Get user
    user = get_user(db, token_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "warehouse_id": user.warehouse_id,
            "role": user.role.name,
            "role_id": user.role.id,
        }
    )

    # Create new refresh token (optional - could reuse existing)
    new_refresh_token_obj = RefreshTokenService.create_refresh_token(
        db=db, user_id=user.id, device_info=token_obj.user_agent
    )

    # Revoke old refresh token
    RefreshTokenService.revoke_refresh_token(db, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_obj.token,
        "token_type": "bearer",
        "expires_in": 15 * 60,  # 15 minutes in seconds
    }


def logout(db: Session, refresh_token: str) -> bool:
    """
    Logout user by revoking refresh token
    """
    return RefreshTokenService.revoke_refresh_token(db, refresh_token)


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
    warehouse_id: int = None,
    role_id: int = 3,  # Default role 'employee'
) -> dict:
    """
    Register a new user
    """
    from services.user_service import create_user

    # Check if username already exists
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Verify if email already exists
    existing_email = get_user_by_email(db, email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create the user
    user = create_user(
        db=db,
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        warehouse_id=warehouse_id or 1,  # Default demo warehouse
        role_id=role_id,
    )

    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }
