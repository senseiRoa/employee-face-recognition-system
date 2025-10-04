from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.company_service import get_company_by_username
from utils.security import verify_password
from utils.jwt_handler import create_access_token


def login(db: Session, username: str, password: str) -> str:
    company = get_company_by_username(db, username)
    if not company or not verify_password(password, company.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": company.username})
    return access_token
