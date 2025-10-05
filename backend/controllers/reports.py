from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from services import report_service
from dependencies import get_current_user
from models import User

router = APIRouter()


@router.get("/checkins")
def get_checkin_report(
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = report_service.get_employee_checkin_report(
        db, 
        employee_id=employee_id,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return [
        {
            "employee_id": r.employee_id,
            "employee_name": r.employee_name,
            "total_check_ins": r.total_check_ins,
            "total_check_outs": r.total_check_outs,
            "last_event": r.last_event,
            "last_event_time": r.last_event_time.isoformat() if r.last_event_time else None
        }
        for r in results
    ]


@router.get("/warehouse-activity")
def get_warehouse_activity(
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = report_service.get_warehouse_activity_report(
        db,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return [
        {
            "warehouse_id": r.warehouse_id,
            "warehouse_name": r.warehouse_name,
            "total_events": r.total_events,
            "unique_employees": r.unique_employees
        }
        for r in results
    ]


@router.get("/frequent-employees")
def get_frequent_employees(
    warehouse_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = report_service.get_frequent_employees(
        db,
        warehouse_id=warehouse_id,
        days=days,
        limit=limit
    )
    
    return [
        {
            "employee_id": r.id,
            "employee_name": r.name,
            "total_events": r.total_events
        }
        for r in results
    ]
