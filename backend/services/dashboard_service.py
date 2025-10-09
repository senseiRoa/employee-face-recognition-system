"""
Servicio para funcionalidades del Dashboard
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from models import Company, Employee, AccessLog, Warehouse, User
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class DashboardService:
    """Servicio para operaciones del dashboard"""

    def __init__(self, db: Session):
        self.db = db

    async def get_stats(self, current_user: User) -> Dict[str, Any]:
        """Obtener estadísticas generales del dashboard"""
        today = datetime.now().date()

        # Filtrar por compañía si aplica
        company_filter = self.get_company_filter(current_user)

        # Filtrar por warehouse del usuario si no es admin
        warehouse_filter = self._get_warehouse_filter(current_user)

        # Total empleados
        total_employees_query = self.db.query(Employee)
        if company_filter is not None:
            total_employees_query = total_employees_query.join(Warehouse).filter(
                company_filter
            )
        if warehouse_filter is not None:
            total_employees_query = total_employees_query.filter(warehouse_filter)
        total_employees = total_employees_query.count()

        # Empleados activos
        active_employees = total_employees_query.filter(
            Employee.is_active == True
        ).count()

        # Total warehouses and companies
        if current_user.role.name == "admin":
            total_companies = self.db.query(Company).count()

            total_warehouses = self.db.query(Warehouse).count()
            active_warehouses = (
                self.db.query(Warehouse).filter(Warehouse.is_active == True).count()
            )
        else:
            total_companies = 1
            total_warehouses = 1
            active_warehouses = 1 if current_user.warehouse.is_active else 0

        # Clock-ins/outs de hoy
        today_logs_query = self.db.query(AccessLog).filter(
            func.date(AccessLog.timestamp) == today
        )

        if warehouse_filter is not None:
            today_logs_query = today_logs_query.join(Employee).filter(warehouse_filter)

        todays_checkins = today_logs_query.filter(AccessLog.event_type == "in").count()
        todays_checkouts = today_logs_query.filter(
            AccessLog.event_type == "out"
        ).count()

        # Calcular promedio de horas (simplificado)
        avg_daily_hours = self._calculate_avg_daily_hours(warehouse_filter)

        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "total_warehouses": total_warehouses,
            "total_companies": total_companies,
            "active_warehouses": active_warehouses,
            "todays_checkins": todays_checkins,
            "todays_checkouts": todays_checkouts,
            "pending_checkouts": todays_checkins - todays_checkouts,
            "avg_daily_hours": avg_daily_hours,
        }

    async def get_recent_activities(
        self, current_user: User, limit: int = 10
    ) -> Dict[str, Any]:
        """Obtener actividades recientes"""
        query = self.db.query(AccessLog).join(Employee).join(Warehouse)

        warehouse_filter = self._get_warehouse_filter(current_user)
        if warehouse_filter is not None:
            query = query.filter(warehouse_filter)

        # Obtener actividades ordenadas por fecha más reciente
        activities = query.order_by(desc(AccessLog.timestamp)).limit(limit).all()
        total = query.count()

        activities_list = []
        for log in activities:
            activities_list.append(
                {
                    "id": log.id,
                    "employee_id": log.employee_id,
                    "employee_name": f"{log.employee.first_name} {log.employee.last_name}",
                    "warehouse_name": log.employee.warehouse.name,
                    "action": "clock_in" if log.event_type == "in" else "clock_out",
                    "timestamp": log.timestamp,
                    "recognition_confidence": log.confidence_score
                    if log.confidence_score
                    else 0.85,
                    "photo_url": f"/uploads/faces/check_{log.id}.jpg"
                    if log.confidence_score
                    else None,
                }
            )

        return {"activities": activities_list, "total": total}

    async def get_attendance_chart(
        self, current_user: User, days: int = 7
    ) -> Dict[str, Any]:
        """Obtener datos para gráfico de asistencia"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        warehouse_filter = self._get_warehouse_filter(current_user)

        # Obtener datos para cada día
        labels = []
        checkins_data = []
        checkouts_data = []

        for i in range(days):
            current_date = start_date + timedelta(days=i)

            # Query para clock-ins del día
            checkins_query = self.db.query(AccessLog).filter(
                and_(
                    func.date(AccessLog.timestamp) == current_date,
                    AccessLog.event_type == "in",
                )
            )

            # Query para clock-outs del día
            checkouts_query = self.db.query(AccessLog).filter(
                and_(
                    func.date(AccessLog.timestamp) == current_date,
                    AccessLog.event_type == "out",
                )
            )

            # Aplicar filtro de warehouse si es necesario
            if warehouse_filter is not None:
                checkins_query = checkins_query.join(Employee).filter(warehouse_filter)
                checkouts_query = checkouts_query.join(Employee).filter(
                    warehouse_filter
                )

            checkins_count = checkins_query.count()
            checkouts_count = checkouts_query.count()

            # Formatear etiqueta del día
            if days <= 7:
                label = current_date.strftime("%a")  # Mon, Tue, etc.
            else:
                label = current_date.strftime("%m/%d")  # 10/07, etc.

            labels.append(label)
            checkins_data.append(checkins_count)
            checkouts_data.append(checkouts_count)

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Clock-ins",
                    "data": checkins_data,
                    "backgroundColor": "rgba(59, 130, 246, 0.8)",
                },
                {
                    "label": "Clock-outs",
                    "data": checkouts_data,
                    "backgroundColor": "rgba(16, 185, 129, 0.8)",
                },
            ],
        }

    async def get_warehouse_chart(self, current_user: User) -> Dict[str, Any]:
        """Obtener datos para gráfico de distribución de almacenes"""
        if current_user.role.name == "admin":
            # Admin ve todos los warehouses
            warehouses = (
                self.db.query(Warehouse).filter(Warehouse.is_active == True).all()
            )
        else:
            # Otros roles solo ven su warehouse
            warehouses = [current_user.warehouse]

        labels = []
        data = []
        colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"]

        total_employees = 0

        for i, warehouse in enumerate(warehouses):
            employee_count = (
                self.db.query(Employee)
                .filter(
                    and_(
                        Employee.warehouse_id == warehouse.id,
                        Employee.is_active == True,
                    )
                )
                .count()
            )

            labels.append(warehouse.name)
            data.append(employee_count)
            total_employees += employee_count

        # Asegurar que tenemos suficientes colores
        chart_colors = colors[: len(warehouses)]
        if len(warehouses) > len(colors):
            chart_colors.extend(["#6b7280"] * (len(warehouses) - len(colors)))

        return {
            "labels": labels,
            "data": data,
            "colors": chart_colors,
            "total_employees": total_employees,
        }

    def _get_warehouse_filter(self, current_user: User):
        """Obtener filtro de warehouse según el rol del usuario"""
        if current_user.role.name == "admin":
            return None  # Admin ve todo
        return Employee.warehouse_id == current_user.warehouse_id

    def get_company_filter(self, current_user: User):
        """Obtener filtro de compañía según el usuario (placeholder para multi-compañía)"""
        if current_user.role.name == "admin":
            return None  # Admin ve todo
        return Employee.warehouse.company_id == current_user.warehouse.company_id

    def _calculate_avg_daily_hours(self, warehouse_filter) -> str:
        """Calcular promedio de horas diarias (implementación simplificada)"""
        # TODO: Implementar cálculo real basado en logs de entrada/salida
        # Por ahora devolvemos un valor fijo
        return "8.2h"  # todo: calcular realmente
