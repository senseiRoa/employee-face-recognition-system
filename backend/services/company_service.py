from sqlalchemy.orm import Session
from typing import List, Optional
from models import Company
import datetime


def create_company(
    db: Session, name: str, email: str = None, phone: str = None, address: str = None
) -> Company:
    """
    Create a new company
    """
    db_company = Company(
        name=name,
        email=email,
        phone=phone,
        address=address,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_company(db: Session, company_id: int) -> Optional[Company]:
    """
    Get company by ID
    """
    return db.query(Company).filter(Company.id == company_id).first()


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    """
    Get list of companies
    """
    return db.query(Company).offset(skip).limit(limit).all()


def update_company(
    db: Session,
    company_id: int,
    name: str = None,
    email: str = None,
    phone: str = None,
    address: str = None,
) -> Optional[Company]:
    """
    Update an existing company
    """
    db_company = get_company(db, company_id)
    if not db_company:
        return None

    if name is not None:
        db_company.name = name
    if email is not None:
        db_company.email = email
    if phone is not None:
        db_company.phone = phone
    if address is not None:
        db_company.address = address

    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> bool:
    """
    Delete a company
    """
    db_company = get_company(db, company_id)
    if not db_company:
        return False

    db.delete(db_company)
    db.commit()
    return True



