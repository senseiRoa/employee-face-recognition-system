"""
Servicio para funcionalidades de Reports
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from models import Employee, AccessLog, Warehouse, User
from schemas.report_schemas import ReportGenerateRequest, ReportType
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import io


class ReportService:
    """Servicio para operaciones de reportes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_stats(self, current_user: User) -> Dict[str, Any]:
        """Obtener estadísticas para la vista de reportes"""
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        warehouse_filter = self._get_warehouse_filter(current_user)
        
        # Total empleados
        total_employees_query = self.db.query(Employee)
        if warehouse_filter is not None:
            total_employees_query = total_employees_query.filter(warehouse_filter)
        total_employees = total_employees_query.count()
        
        # Check-ins de hoy
        today_checkins_query = self.db.query(AccessLog).filter(
            and_(
                func.date(AccessLog.ts) == today,
                AccessLog.event == 'in'
            )
        )
        if warehouse_filter is not None:
            today_checkins_query = today_checkins_query.join(Employee).filter(warehouse_filter)
        total_checkins_today = today_checkins_query.count()
        
        # Warehouses activos
        if current_user.role.name == 'admin':
            active_warehouses = self.db.query(Warehouse).filter(Warehouse.is_active).count()
        else:
            active_warehouses = 1 if current_user.warehouse.is_active else 0
        
        # Top warehouse (el que más check-ins tiene este mes)
        top_warehouse = self._get_top_warehouse(month_start, warehouse_filter)
        
        return {
            "total_employees": total_employees,
            "total_checkins_today": total_checkins_today,
            "active_warehouses": active_warehouses,
            "avg_working_hours": "8.2h",  # Simplificado
            "monthly_attendance_rate": 94.5,  # Simplificado
            "top_warehouse": top_warehouse,
            "reports_generated_this_month": 23  # Simplificado - implementar con tabla de reportes
        }
    
    async def generate_report(
        self, 
        request: ReportGenerateRequest, 
        current_user: User
    ) -> Tuple[bytes, str, str]:
        """Generar reporte según parámetros"""
        
        # Obtener datos según tipo de reporte
        data = await self._get_report_data(request, current_user)
        
        # Por ahora generar un reporte simple
        if request.format.value == 'csv':
            content = self._generate_csv_content(data, request)
            content_type = 'text/csv'
            extension = 'csv'
        elif request.format.value == 'excel':
            content = self._generate_excel_content(data, request)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            extension = 'xlsx'
        else:  # pdf
            content = self._generate_pdf_content(data, request)
            content_type = 'application/pdf'
            extension = 'pdf'
        
        filename = f"reporte_{request.type.value}_{request.date_from}_{request.date_to}.{extension}"
        
        return content, filename, content_type
    
    async def get_recent_reports(self, current_user: User, limit: int = 10) -> Dict[str, Any]:
        """Obtener reportes recientes generados"""
        # Por ahora devolver datos mock - implementar con tabla de reportes
        mock_reports = [
            {
                "id": 1,
                "name": "Weekly Attendance Report",
                "description": "Employee attendance Oct 1-7",
                "type": "attendance",
                "format": "pdf",
                "created_at": datetime.now() - timedelta(days=1),
                "created_by": current_user.username,
                "created_by_name": f"{current_user.first_name} {current_user.last_name}",
                "file_size": "2.5MB",
                "download_url": "/api/reports/1/download",
                "parameters": {
                    "date_from": "2025-10-01",
                    "date_to": "2025-10-07",
                    "warehouse_id": None
                }
            }
        ]
        
        return {
            "reports": mock_reports[:limit],
            "total": len(mock_reports)
        }
    
    async def download_report(
        self, 
        report_id: int, 
        current_user: User
    ) -> Tuple[bytes, str, str]:
        """Descargar reporte específico"""
        # Por ahora generar contenido mock
        content = b"Mock report content for report " + str(report_id).encode()
        filename = f"report_{report_id}.pdf"
        content_type = "application/pdf"
        
        return content, filename, content_type
    
    def _get_warehouse_filter(self, current_user: User):
        """Obtener filtro de warehouse según el rol del usuario"""
        if current_user.role.name == 'admin':
            return None
        return Employee.warehouse_id == current_user.warehouse_id
    
    def _get_top_warehouse(self, month_start, warehouse_filter) -> str:
        """Obtener el warehouse con más check-ins este mes"""
        # Simplificado
        return "Central Warehouse"
    
    def _generate_csv_content(self, data: List[Dict], request: ReportGenerateRequest) -> bytes:
        """Generar contenido CSV"""
        if not data:
            return b"No data available"
        
        import csv
        import io
        
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return output.getvalue().encode('utf-8')
    
    def _generate_excel_content(self, data: List[Dict], request: ReportGenerateRequest) -> bytes:
        """Generar contenido Excel"""
        import pandas as pd
        
        if not data:
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        
        return output.getvalue()
    
    def _generate_pdf_content(self, data: List[Dict], request: ReportGenerateRequest) -> bytes:
        """Generar contenido PDF"""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Título
        p.drawString(100, 750, f"Report: {request.type.value.title()}")
        p.drawString(100, 730, f"Date Range: {request.date_from} to {request.date_to}")
        
        # Datos simplificados
        y = 700
        p.drawString(100, y, f"Total records: {len(data)}")
        
        if data:
            y -= 20
            p.drawString(100, y, "Sample data:")
            y -= 20
            
            # Mostrar primeros 5 registros
            for i, record in enumerate(data[:5]):
                if y < 100:  # Nueva página si es necesario
                    p.showPage()
                    y = 750
                
                record_str = " | ".join([f"{k}: {v}" for k, v in list(record.items())[:3]])
                p.drawString(100, y, record_str[:80] + "..." if len(record_str) > 80 else record_str)
                y -= 15
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    async def _get_report_data(self, request: ReportGenerateRequest, current_user: User) -> List[Dict]:
        """Obtener datos para el reporte según el tipo"""
        warehouse_filter = self._get_warehouse_filter(current_user)
        
        if request.type == ReportType.ATTENDANCE:
            return self._get_attendance_data(request, warehouse_filter)
        elif request.type == ReportType.EMPLOYEES:
            return self._get_employees_data(request, warehouse_filter)
        elif request.type == ReportType.WAREHOUSES:
            return self._get_warehouses_data(request, warehouse_filter)
        else:  # ACTIVITY
            return self._get_activity_data(request, warehouse_filter)
    
    def _get_attendance_data(self, request: ReportGenerateRequest, warehouse_filter) -> List[Dict]:
        """Obtener datos de asistencia"""
        query = self.db.query(AccessLog).join(Employee).filter(
            and_(
                func.date(AccessLog.ts) >= request.date_from,
                func.date(AccessLog.ts) <= request.date_to
            )
        )
        
        if warehouse_filter is not None:
            query = query.filter(warehouse_filter)
        
        if request.warehouse_id:
            query = query.filter(Employee.warehouse_id == request.warehouse_id)
        
        if request.employee_id:
            query = query.filter(Employee.id == request.employee_id)
        
        logs = query.order_by(AccessLog.ts).all()
        
        # Convertir a formato para reporte
        data = []
        for log in logs:
            data.append({
                "date": log.ts.strftime("%Y-%m-%d"),
                "time": log.ts.strftime("%H:%M:%S"),
                "employee_name": f"{log.employee.first_name} {log.employee.last_name}",
                "warehouse": log.employee.warehouse.name,
                "action": log.event,
                "confidence": log.distance or 0.0
            })
        
        return data
    
    def _get_employees_data(self, request: ReportGenerateRequest, warehouse_filter) -> List[Dict]:
        """Obtener datos de empleados"""
        query = self.db.query(Employee).join(Warehouse)
        
        if warehouse_filter is not None:
            query = query.filter(warehouse_filter)
        
        if request.warehouse_id:
            query = query.filter(Employee.warehouse_id == request.warehouse_id)
        
        employees = query.all()
        
        data = []
        for emp in employees:
            data.append({
                "id": emp.id,
                "name": f"{emp.first_name} {emp.last_name}",
                "warehouse": emp.warehouse.name,
                "status": "Active" if emp.is_active else "Inactive",
                "created_at": emp.created_at.strftime("%Y-%m-%d")
            })
        
        return data
    
    def _get_warehouses_data(self, request: ReportGenerateRequest, warehouse_filter) -> List[Dict]:
        """Obtener datos de warehouses"""
        query = self.db.query(Warehouse)
        
        if warehouse_filter is not None and hasattr(warehouse_filter, 'right'):
            # Filtrar solo el warehouse del usuario
            warehouse_id = warehouse_filter.right.value
            query = query.filter(Warehouse.id == warehouse_id)
        
        warehouses = query.all()
        
        data = []
        for wh in warehouses:
            employee_count = self.db.query(Employee).filter(
                Employee.warehouse_id == wh.id
            ).count()
            
            data.append({
                "id": wh.id,
                "name": wh.name,
                "address": wh.address or "N/A",
                "employee_count": employee_count,
                "status": "Active" if wh.is_active else "Inactive"
            })
        
        return data
    
    def _get_activity_data(self, request: ReportGenerateRequest, warehouse_filter) -> List[Dict]:
        """Obtener datos de actividad general"""
        return self._get_attendance_data(request, warehouse_filter)
