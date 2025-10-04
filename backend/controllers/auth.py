from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import CompanyCreate, LoginReq, Token
from services import auth_service, company_service
from database import get_db

router = APIRouter()


@router.post("/register", response_model=Token)
def register_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = company_service.get_company_by_username(db, username=company.username)
    if db_company:
        raise HTTPException(status_code=400, detail="Username already registered")
    company_service.create_company(db=db, company=company)
    access_token = auth_service.login(
        db, username=company.username, password=company.password
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: LoginReq, db: Session = Depends(get_db)):
    access_token = auth_service.login(
        db, username=form_data.username, password=form_data.password
    )
    return {"access_token": access_token, "token_type": "bearer"}
