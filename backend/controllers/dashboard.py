"""
Controlador para endpoints de Dashboard
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from services.dashboard_service import DashboardService
from schemas.dashboard_schemas import (
    DashboardStatsResponse,
    RecentActivitiesResponse,
    AttendanceChartResponse,
    WarehouseChartResponse,
)
from utils.permission_decorators import require_dashboard_read
from models import User

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(require_dashboard_read), db: Session = Depends(get_db)
):
    """
    Obtener estadísticas generales del dashboard
    """
    service = DashboardService(db)
    return await service.get_stats(current_user)


@router.get("/recent-activities", response_model=RecentActivitiesResponse)
async def get_recent_activities(
    limit: int = 10,
    current_user: User = Depends(require_dashboard_read),
    db: Session = Depends(get_db),
):
    """
    Obtener actividades recientes de check-in/out
    """
    service = DashboardService(db)
    return await service.get_recent_activities(current_user, limit)


@router.get("/charts/attendance", response_model=AttendanceChartResponse)
async def get_attendance_chart(
    days: int = 7,
    current_user: User = Depends(require_dashboard_read),
    db: Session = Depends(get_db),
):
    """
    Obtener datos para gráfico de asistencia
    """
    service = DashboardService(db)
    return await service.get_attendance_chart(current_user, days)


@router.get("/charts/warehouses", response_model=WarehouseChartResponse)
async def get_warehouse_chart(
    current_user: User = Depends(require_dashboard_read), db: Session = Depends(get_db)
):
    """
    Obtener datos para gráfico de distribución de almacenes
    """
    service = DashboardService(db)
    return await service.get_warehouse_chart(current_user)
