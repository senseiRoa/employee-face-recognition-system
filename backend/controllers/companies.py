from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from services import company_service
from dependencies import get_current_user, require_admin
from models import User

router = APIRouter()


# Esquemas para respuestas
class CompanyResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@router.get("/me", response_model=CompanyResponse)
def get_my_company(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Obtener información de la compañía del usuario actual
    """
    return current_user.company


@router.get("/", response_model=List[CompanyResponse])
def get_companies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Obtener lista de compañías (solo admins)
    """
    companies = company_service.get_companies(db, skip=skip, limit=limit)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener información de una compañía específica
    """
    # Solo admin puede ver cualquier compañía, otros solo pueden ver la suya
    if current_user.role.name != "admin" and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this company",
        )

    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualizar información de una compañía
    """
    # Solo admin puede actualizar cualquier compañía, managers solo pueden actualizar la suya
    if current_user.role.name not in ["admin", "manager"] or (
        current_user.role.name == "manager" and current_user.company_id != company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this company",
        )

    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    updated_company = company_service.update_company(
        db=db,
        company_id=company_id,
        name=company_update.name,
        email=company_update.email,
        phone=company_update.phone,
        address=company_update.address,
    )

    return updated_company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Eliminar una compañía (solo admins)
    """
    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    success = company_service.delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete company",
        )
