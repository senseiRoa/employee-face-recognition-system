from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from database import get_db
from services import log_service
from schemas import AccessLogEnhanced, LoginLog, UserLoginLog
from utils.permission_decorators import require_logs_audit, require_tablet_or_logs_audit
from models import User

router = APIRouter()


@router.get("/access", response_model=List[AccessLogEnhanced])
def list_access_logs(
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tablet_or_logs_audit),
):
    """
    List access logs with enhanced information (employee name, warehouse name, etc.)
    """
    return log_service.get_enhanced_access_logs(
        db,
        employee_id=employee_id,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get("/exports")
def export_enhanced_access_logs_excel(
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 1000,  # Higher limit for exports
    db: Session = Depends(get_db),
    current_user: User = Depends(require_logs_audit),
):
    """
    Export access logs as Excel file with enhanced information
    Returns a downloadable Excel file with comprehensive access log data
    """
    # Get the Excel file content and filename from the service
    file_content, filename = log_service.generate_excel_export(
        db,
        employee_id=employee_id,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    # Return as downloadable Excel file
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/login", response_model=List[LoginLog])
def list_login_logs(
    company_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_logs_audit),
):
    """
    List login logs with audit permissions
    """
    return log_service.get_login_logs(
        db,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get("/user-login", response_model=List[UserLoginLog])
def list_user_login_logs(
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_logs_audit),
):
    """
    List user login logs with audit permissions
    """
    return log_service.get_user_login_logs(
        db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
