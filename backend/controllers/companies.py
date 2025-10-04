from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import Company, CompanyUpdate
from services import company_service
from dependencies import get_current_user
from models import Company as CompanyModel

router = APIRouter()


@router.get("/me", response_model=Company)
def get_current_company(
    current_user: CompanyModel = Depends(get_current_user)
):
    return current_user


@router.get("/{company_id}", response_model=Company)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: CompanyModel = Depends(get_current_user)
):
    if current_user.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this company"
        )
    return current_user


@router.put("/{company_id}", response_model=Company)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: CompanyModel = Depends(get_current_user)
):
    if current_user.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this company"
        )
    
    if company_update.username:
        existing = company_service.get_company_by_username(db, company_update.username)
        if existing and existing.id != company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    from utils.security import get_password_hash
    update_data = company_update.dict(exclude_unset=True)
    if 'password' in update_data and update_data['password']:
        update_data['password'] = get_password_hash(update_data['password'])
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: CompanyModel = Depends(get_current_user)
):
    if current_user.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this company"
        )
    
    db.delete(current_user)
    db.commit()
