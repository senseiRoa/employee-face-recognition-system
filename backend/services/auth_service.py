from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.user_service import get_user_by_username, get_user_by_email
from utils.password import verify_password
from utils.jwt_handler import create_access_token


def login(db: Session, username_or_email: str, password: str) -> dict:
    """
    Authenticate user by username or email
    """
    # Try by username first
    user = get_user_by_username(db, username_or_email)

    # If not found by username, try by email
    if not user:
        user = get_user_by_email(db, username_or_email)

    # Check if user exists and password is correct
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    # Create token with user information
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "company_id": user.company_id,
            "role": user.role.name,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name,
            "company_id": user.company_id,
            "company_name": user.company.name,
        },
    }


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    first_name: str = None,
    last_name: str = None,
    company_id: int = None,
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

    # Check if email already exists
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
        company_id=company_id or 1,  # Default demo company
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
