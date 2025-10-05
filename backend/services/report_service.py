from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from models import AccessLog, Employee, Warehouse


def get_employee_checkin_report(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(
        Employee.id.label("employee_id"),
        func.concat(Employee.first_name, ' ', Employee.last_name).label("employee_name"),
        func.sum(func.if_(AccessLog.event == 'in', 1, 0)).label("total_check_ins"),
        func.sum(func.if_(AccessLog.event == 'out', 1, 0)).label("total_check_outs"),
        func.max(AccessLog.event).label("last_event"),
        func.max(AccessLog.ts).label("last_event_time")
    ).join(AccessLog, Employee.id == AccessLog.employee_id)
    
    if employee_id:
        query = query.filter(Employee.id == employee_id)
    if warehouse_id:
        query = query.filter(Employee.warehouse_id == warehouse_id)
    if start_date:
        query = query.filter(AccessLog.ts >= start_date)
    if end_date:
        query = query.filter(AccessLog.ts <= end_date)
    
    query = query.group_by(Employee.id)
    
    return query.all()


def get_warehouse_activity_report(
    db: Session,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(
        Warehouse.id.label("warehouse_id"),
        Warehouse.name.label("warehouse_name"),
        func.count(AccessLog.id).label("total_events"),
        func.count(func.distinct(AccessLog.employee_id)).label("unique_employees")
    ).join(Employee, Warehouse.id == Employee.warehouse_id).join(
        AccessLog, Employee.id == AccessLog.employee_id
    )
    
    if warehouse_id:
        query = query.filter(Warehouse.id == warehouse_id)
    if start_date:
        query = query.filter(AccessLog.ts >= start_date)
    if end_date:
        query = query.filter(AccessLog.ts <= end_date)
    
    query = query.group_by(Warehouse.id)
    
    return query.all()


def get_frequent_employees(
    db: Session,
    warehouse_id: Optional[int] = None,
    days: int = 7,
    limit: int = 10
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        Employee.id,
        func.concat(Employee.first_name, ' ', Employee.last_name).label("name"),
        func.count(AccessLog.id).label("total_events")
    ).join(AccessLog, Employee.id == AccessLog.employee_id)
    
    if warehouse_id:
        query = query.filter(Employee.warehouse_id == warehouse_id)
    
    query = query.filter(AccessLog.ts >= start_date)
    query = query.group_by(Employee.id)
    query = query.order_by(desc("total_events"))
    query = query.limit(limit)
    
    return query.all()
