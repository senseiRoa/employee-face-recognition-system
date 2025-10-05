from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from services import auth_service
from database import get_db

router = APIRouter()


# Esquemas para las requests
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_id: Optional[int] = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario
    """
    try:
        result = auth_service.register_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            company_id=user_data.company_id,
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
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
def get_current_user_info(db: Session = Depends(get_db)):
    """
    Obtener información del usuario actual
    (requiere implementar dependencia de autenticación)
    """
    # TODO: Implementar cuando se tenga la dependencia de usuario actual
    return {"message": "Endpoint para obtener información del usuario actual"}
