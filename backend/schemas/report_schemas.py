"""
Schemas para endpoints de Reports
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class ReportType(str, Enum):
    """Tipos de reportes disponibles"""

    ATTENDANCE = "attendance"
    EMPLOYEES = "employees"
    WAREHOUSES = "warehouses"
    ACTIVITY = "activity"


class ReportFormat(str, Enum):
    """Formatos de reporte disponibles"""

    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"


class GroupBy(str, Enum):
    """Opciones de agrupación"""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class ReportGenerateRequest(BaseModel):
    """Request para generar reporte"""

    type: ReportType
    date_from: date
    date_to: date
    format: ReportFormat
    warehouse_id: Optional[int] = None
    employee_id: Optional[int] = None
    include_photos: bool = False
    group_by: GroupBy = GroupBy.DAY


class ReportStatsResponse(BaseModel):
    """Estadísticas para la vista de reportes"""

    total_employees: int
    total_checkins_today: int
    active_warehouses: int
    avg_working_hours: str
    monthly_attendance_rate: float
    top_warehouse: str
    reports_generated_this_month: int


class ReportItem(BaseModel):
    """Item de reporte en la lista"""

    id: int
    name: str
    description: str
    type: ReportType
    format: ReportFormat
    created_at: datetime
    created_by: str
    created_by_name: str
    file_size: str
    download_url: str
    parameters: Dict[str, Any]


class RecentReportsResponse(BaseModel):
    """Respuesta con reportes recientes"""

    reports: List[ReportItem]
    total: int


class ReportChartDataset(BaseModel):
    """Dataset para gráficos en reportes"""

    label: str
    data: List[int]
    backgroundColor: str


class ReportChartResponse(BaseModel):
    """Respuesta para gráficos en reportes"""

    labels: List[str]
    datasets: List[ReportChartDataset]
    summary: Optional[Dict[str, Any]] = None


class WarehouseReportDataset(BaseModel):
    """Dataset para gráfico de warehouses en reportes"""

    label: str
    data: List[int]
    backgroundColor: List[str]


class WarehouseReportChartResponse(BaseModel):
    """Respuesta para gráfico de warehouses en reportes"""

    labels: List[str]
    datasets: List[WarehouseReportDataset]
