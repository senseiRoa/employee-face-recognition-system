"""
Controlador para endpoints de Reports
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import io

from database import get_db
from dependencies import get_current_user
from services.report_service import ReportService
from schemas.report_schemas import (
    ReportStatsResponse,
    ReportGenerateRequest,
    RecentReportsResponse,
    ReportChartResponse,
    WarehouseReportChartResponse
)
from utils.permission_decorators import require_reports_analytics_read
from models import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/stats", response_model=ReportStatsResponse)
async def get_report_stats(
    current_user: User = Depends(require_reports_analytics_read),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas para la vista de reportes
    """
    service = ReportService(db)
    return await service.get_stats(current_user)


@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(require_reports_analytics_read),
    db: Session = Depends(get_db)
):
    """
    Generar reporte personalizado
    """
    service = ReportService(db)
    file_content, filename, content_type = await service.generate_report(
        request, current_user
    )
    
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/recent", response_model=RecentReportsResponse)
async def get_recent_reports(
    limit: int = 10,
    current_user: User = Depends(require_reports_analytics_read),
    db: Session = Depends(get_db)
):
    """
    Obtener reportes recientes generados
    """
    service = ReportService(db)
    return await service.get_recent_reports(current_user, limit)


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(require_reports_analytics_read),
    db: Session = Depends(get_db)
):
    """
    Descargar reporte específico
    """
    service = ReportService(db)
    file_content, filename, content_type = await service.download_report(
        report_id, current_user
    )
    
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/charts/attendance", response_model=ReportChartResponse)
async def get_attendance_chart(
    days: int = 30,
    warehouse_id: Optional[int] = None,
    group_by: str = "week",
    current_user: User = Depends(require_reports_analytics_read),
    db: Session = Depends(get_db)
):
    """
    Obtener datos para gráficos de asistencia en reportes
    """
    service = ReportService(db)
    return await service.get_attendance_chart(current_user, days, warehouse_id, group_by)


@router.get("/charts/warehouses", response_model=WarehouseReportChartResponse)
async def get_warehouse_chart(
    current_user: User = Depends(require_reports_analytics_read),
    db: Session = Depends(get_db)
):
    """
    Obtener datos para gráfico de distribución de almacenes en reportes
    """
    service = ReportService(db)
    return await service.get_warehouse_chart(current_user)
