from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from database import get_db
from services import company_service
from dependencies import get_current_user, require_admin
from models import User

router = APIRouter()


# Esquemas de entrada
class CompanyCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[bool] = True

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")
        return v.strip()

    @validator("phone")
    def validate_phone(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("Phone number must be at least 10 characters")
        return v.strip() if v else None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[bool] = None

    @validator("name")
    def validate_name(cls, v):
        if v is not None and (not v or len(v.strip()) < 2):
            raise ValueError("Company name must be at least 2 characters")
        return v.strip() if v else None

    @validator("phone")
    def validate_phone(cls, v):
        if v is not None and v and len(v.strip()) < 10:
            raise ValueError("Phone number must be at least 10 characters")
        return v.strip() if v else None


# Esquemas de respuesta
class CompanyResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    warehouses_count: Optional[int] = None

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Endpoints
@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new company (admins only)
    """
    # Check if company name already exists
    if company_service.company_exists_by_name(db, company_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A company with this name already exists",
        )

    try:
        new_company = company_service.create_company(
            db=db,
            name=company_data.name,
            email=company_data.email,
            phone=company_data.phone,
            address=company_data.address,
            status=company_data.status,
        )

        # Add warehouses count
        response_data = CompanyResponse.from_orm(new_company)
        response_data.warehouses_count = (
            len(new_company.warehouses) if new_company.warehouses else 0
        )

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create company: {str(e)}",
        )


@router.get("/", response_model=CompanyListResponse)
def get_companies(
    skip: int = Query(0, ge=0, description="Number of companies to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of companies to return"),
    status: Optional[bool] = Query(
        None, description="Filter by status (true=active, false=inactive)"
    ),
    search: Optional[str] = Query(None, description="Search in name, email or address"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of companies with pagination and filtering
    """
    # Non-admin users can only see their own company
    if current_user.role.name != "admin":
        if current_user.company_id:
            company = company_service.get_company(db, current_user.company_id)
            if company:
                return CompanyListResponse(
                    companies=[CompanyResponse.from_orm(company)],
                    total=1,
                    page=1,
                    per_page=1,
                    total_pages=1,
                )
        return CompanyListResponse(
            companies=[], total=0, page=1, per_page=limit, total_pages=0
        )

    # Get companies with filtering
    companies = company_service.get_companies(
        db, skip=skip, limit=limit, status=status, search=search
    )
    total = company_service.get_companies_count(db, status=status, search=search)

    # Add warehouses count to each company
    companies_response = []
    for company in companies:
        company_data = CompanyResponse.from_orm(company)
        company_data.warehouses_count = (
            len(company.warehouses) if company.warehouses else 0
        )
        companies_response.append(company_data)

    total_pages = (total + limit - 1) // limit
    page = (skip // limit) + 1

    return CompanyListResponse(
        companies=companies_response,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages,
    )


@router.get("/me", response_model=CompanyResponse)
def get_my_company(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get information of the current user's company
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any company",
        )

    company = company_service.get_company(db, current_user.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    response_data = CompanyResponse.from_orm(company)
    response_data.warehouses_count = (
        len(company.warehouses) if company.warehouses else 0
    )

    return response_data


@router.get("/active", response_model=List[CompanyResponse])
def get_active_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get list of active companies (admins only)
    """
    companies = company_service.get_active_companies(db, skip=skip, limit=limit)

    companies_response = []
    for company in companies:
        company_data = CompanyResponse.from_orm(company)
        company_data.warehouses_count = (
            len(company.warehouses) if company.warehouses else 0
        )
        companies_response.append(company_data)

    return companies_response


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get information of a specific company
    """
    # Only admin can view any company, others can only view their own
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

    response_data = CompanyResponse.from_orm(company)
    response_data.warehouses_count = (
        len(company.warehouses) if company.warehouses else 0
    )

    return response_data


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update company information
    """
    # Only admin can update any company, managers can only update their own
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

    # Check if new name already exists (if name is being updated)
    if company_update.name and company_service.company_exists_by_name(
        db, company_update.name, exclude_id=company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A company with this name already exists",
        )

    try:
        updated_company = company_service.update_company(
            db=db,
            company_id=company_id,
            name=company_update.name,
            email=company_update.email,
            phone=company_update.phone,
            address=company_update.address,
            status=company_update.status,
        )

        if not updated_company:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update company",
            )

        response_data = CompanyResponse.from_orm(updated_company)
        response_data.warehouses_count = (
            len(updated_company.warehouses) if updated_company.warehouses else 0
        )

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update company: {str(e)}",
        )


@router.patch("/{company_id}/toggle-status", response_model=CompanyResponse)
def toggle_company_status(
    company_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Toggle company status (active/inactive) - admins only
    """
    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    try:
        updated_company = company_service.toggle_company_status(db, company_id)
        if not updated_company:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle company status",
            )

        response_data = CompanyResponse.from_orm(updated_company)
        response_data.warehouses_count = (
            len(updated_company.warehouses) if updated_company.warehouses else 0
        )

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle company status: {str(e)}",
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Hard delete a company - PERMANENT (admins only)
    """
    company = company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    # Check if company has related data (warehouses, employees)
    if company.warehouses and len(company.warehouses) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete company with associated warehouses. Remove warehouses first or use soft delete.",
        )

    try:
        success = company_service.delete_company(db, company_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete company",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete company: {str(e)}",
        )
