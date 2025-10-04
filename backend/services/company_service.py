from sqlalchemy.orm import Session
from models import Company
from schemas import CompanyCreate
from utils.security import get_password_hash


def create_company(db: Session, company: CompanyCreate) -> Company:
    hashed_password = get_password_hash(company.password)
    db_company = Company(
        username=company.username, name=company.name, password=hashed_password
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_company_by_username(db: Session, username: str) -> Company:
    return db.query(Company).filter(Company.username == username).first()
