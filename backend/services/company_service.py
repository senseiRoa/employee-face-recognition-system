from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from models import Company
import datetime


def create_company(
    db: Session,
    name: str,
    email: str = None,
    phone: str = None,
    address: str = None,
    status: bool = True,
    user_timezone: str = "UTC",
) -> Company:
    """
    Create a new company
    """
    db_company = Company(
        name=name,
        email=email,
        phone=phone,
        address=address,
        status=status,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
        record_timezone=user_timezone,
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


def get_companies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[Company]:
    """
    Get list of companies with optional filtering
    """
    query = db.query(Company)

    # Filter by status if provided
    if status is not None:
        query = query.filter(Company.status == status)

    # Search by name, email or address if provided
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Company.name.ilike(search_filter),
                Company.email.ilike(search_filter),
                Company.address.ilike(search_filter),
            )
        )

    return query.offset(skip).limit(limit).all()


def get_companies_count(
    db: Session, status: Optional[bool] = None, search: Optional[str] = None
) -> int:
    """
    Get total count of companies with optional filtering
    """
    query = db.query(Company)

    if status is not None:
        query = query.filter(Company.status == status)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Company.name.ilike(search_filter),
                Company.email.ilike(search_filter),
                Company.address.ilike(search_filter),
            )
        )

    return query.count()


def get_active_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    """
    Get only active companies
    """
    return (
        db.query(Company).filter(Company.status == True).offset(skip).limit(limit).all()
    )


def update_company(
    db: Session,
    company_id: int,
    name: str = None,
    email: str = None,
    phone: str = None,
    address: str = None,
    status: bool = None,
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
    if status is not None:
        db_company.status = status

    db_company.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(db_company)
    return db_company


def toggle_company_status(db: Session, company_id: int) -> Optional[Company]:
    """
    Toggle company status (active/inactive)
    """
    db_company = get_company(db, company_id)
    if not db_company:
        return None

    db_company.status = not db_company.status
    db_company.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> bool:
    """
    Hard delete a company (only for admins)
    """
    db_company = get_company(db, company_id)
    if not db_company:
        return False

    db.delete(db_company)
    db.commit()
    return True


def company_exists_by_name(db: Session, name: str, exclude_id: int = None) -> bool:
    """
    Check if a company with the given name already exists
    """
    query = db.query(Company).filter(Company.name == name)

    if exclude_id:
        query = query.filter(Company.id != exclude_id)

    return query.first() is not None
