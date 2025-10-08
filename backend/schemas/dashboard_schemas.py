"""
Schemas para endpoints de Dashboard
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DashboardStatsResponse(BaseModel):
    """Respuesta con estadísticas del dashboard"""

    total_employees: int
    active_employees: int
    total_warehouses: int
    total_companies: int
    active_warehouses: int
    todays_checkins: int
    todays_checkouts: int
    pending_checkouts: int
    avg_daily_hours: str


class ActivityItem(BaseModel):
    """Item de actividad reciente"""

    id: int
    employee_id: int
    employee_name: str
    warehouse_name: str
    action: str
    timestamp: datetime
    recognition_confidence: float
    photo_url: Optional[str] = None


class RecentActivitiesResponse(BaseModel):
    """Respuesta con actividades recientes"""

    activities: List[ActivityItem]
    total: int


class ChartDataset(BaseModel):
    """Dataset para gráficos"""

    label: str
    data: List[int]
    backgroundColor: str


class AttendanceChartResponse(BaseModel):
    """Respuesta para gráfico de asistencia"""

    labels: List[str]
    datasets: List[ChartDataset]


class WarehouseChartResponse(BaseModel):
    """Respuesta para gráfico de almacenes"""

    labels: List[str]
    data: List[int]
    colors: List[str]
    total_employees: int
