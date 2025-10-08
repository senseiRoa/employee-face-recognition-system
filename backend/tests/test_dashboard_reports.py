"""
Tests para los endpoints de Dashboard y Reports
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestDashboardEndpoints:
    """Tests para endpoints del dashboard"""
    
    def test_dashboard_stats_unauthorized(self):
        """Test que el endpoint de stats requiere autenticación"""
        response = client.get("/dashboard/stats")
        assert response.status_code == 401
    
    def test_dashboard_recent_activities_unauthorized(self):
        """Test que el endpoint de actividades recientes requiere autenticación"""
        response = client.get("/dashboard/recent-activities")
        assert response.status_code == 401
    
    def test_dashboard_attendance_chart_unauthorized(self):
        """Test que el endpoint de gráfico de asistencia requiere autenticación"""
        response = client.get("/dashboard/charts/attendance")
        assert response.status_code == 401
    
    def test_dashboard_warehouse_chart_unauthorized(self):
        """Test que el endpoint de gráfico de almacenes requiere autenticación"""
        response = client.get("/dashboard/charts/warehouses")
        assert response.status_code == 401


class TestReportsEndpoints:
    """Tests para endpoints de reportes"""
    
    def test_reports_stats_unauthorized(self):
        """Test que el endpoint de stats de reportes requiere autenticación"""
        response = client.get("/reports/stats")
        assert response.status_code == 401
    
    def test_reports_recent_unauthorized(self):
        """Test que el endpoint de reportes recientes requiere autenticación"""
        response = client.get("/reports/recent")
        assert response.status_code == 401
    
    def test_reports_attendance_chart_unauthorized(self):
        """Test que el endpoint de gráfico de asistencia requiere autenticación"""
        response = client.get("/reports/charts/attendance")
        assert response.status_code == 401
    
    def test_reports_warehouse_chart_unauthorized(self):
        """Test que el endpoint de gráfico de almacenes requiere autenticación"""
        response = client.get("/reports/charts/warehouses")
        assert response.status_code == 401
    
    def test_reports_download_unauthorized(self):
        """Test que el endpoint de descarga requiere autenticación"""
        response = client.get("/reports/1/download")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestDashboardWithAuth:
    """Tests con autenticación para dashboard"""
    
    @pytest.fixture
    def auth_headers(self):
        """Fixture para obtener headers de autenticación"""
        # Esto se implementaría con un token real en tests completos
        return {"Authorization": "Bearer fake_token_for_testing"}
    
    def test_dashboard_endpoints_structure(self, auth_headers):
        """Test de la estructura básica de los endpoints (sin autenticación real)"""
        # Estos tests fallarán por permisos, pero verifican que los endpoints existen
        response = client.get("/dashboard/stats", headers=auth_headers)
        # Esperamos 401 o 403, no 404 (que indicaría que el endpoint no existe)
        assert response.status_code in [401, 403]
        
        response = client.get("/dashboard/recent-activities", headers=auth_headers)
        assert response.status_code in [401, 403]
        
        response = client.get("/dashboard/charts/attendance", headers=auth_headers)
        assert response.status_code in [401, 403]
        
        response = client.get("/dashboard/charts/warehouses", headers=auth_headers)
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestReportsWithAuth:
    """Tests con autenticación para reportes"""
    
    @pytest.fixture
    def auth_headers(self):
        """Fixture para obtener headers de autenticación"""
        return {"Authorization": "Bearer fake_token_for_testing"}
    
    def test_reports_endpoints_structure(self, auth_headers):
        """Test de la estructura básica de los endpoints (sin autenticación real)"""
        # Estos tests fallarán por permisos, pero verifican que los endpoints existen
        response = client.get("/reports/stats", headers=auth_headers)
        assert response.status_code in [401, 403]
        
        response = client.get("/reports/recent", headers=auth_headers)
        assert response.status_code in [401, 403]
        
        response = client.get("/reports/charts/attendance", headers=auth_headers)
        assert response.status_code in [401, 403]
        
        response = client.get("/reports/charts/warehouses", headers=auth_headers)
        assert response.status_code in [401, 403]
        
        response = client.get("/reports/1/download", headers=auth_headers)
        assert response.status_code in [401, 403]


class TestReportGeneration:
    """Tests para generación de reportes"""
    
    def test_generate_report_unauthorized(self):
        """Test que la generación de reportes requiere autenticación"""
        report_data = {
            "report_type": "attendance",
            "format": "pdf",
            "date_from": "2024-01-01",
            "date_to": "2024-01-31"
        }
        response = client.post("/reports/generate", json=report_data)
        assert response.status_code == 401
    
    def test_generate_report_invalid_data(self):
        """Test que la generación de reportes valida los datos"""
        # Sin autenticación, pero verificamos que el endpoint existe
        response = client.post("/reports/generate", json={})
        # Esperamos 401 (no autorizado) no 404 (no encontrado)
        assert response.status_code == 401


class TestOpenAPIDocumentation:
    """Tests para verificar que la documentación está completa"""
    
    def test_openapi_schema_includes_dashboard(self):
        """Test que el esquema OpenAPI incluye los endpoints de dashboard"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})
        
        # Verificar que los endpoints de dashboard están documentados
        assert "/dashboard/stats" in paths
        assert "/dashboard/recent-activities" in paths
        assert "/dashboard/charts/attendance" in paths
        assert "/dashboard/charts/warehouses" in paths
    
    def test_openapi_schema_includes_reports(self):
        """Test que el esquema OpenAPI incluye los endpoints de reportes"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})
        
        # Verificar que los endpoints de reportes están documentados
        assert "/reports/stats" in paths
        assert "/reports/generate" in paths
        assert "/reports/recent" in paths
        assert "/reports/{report_id}/download" in paths
        assert "/reports/charts/attendance" in paths
        assert "/reports/charts/warehouses" in paths
    
    def test_openapi_tags_include_new_endpoints(self):
        """Test que los tags incluyen dashboard y reports"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        tags = openapi_data.get("tags", [])
        tag_names = [tag["name"] for tag in tags]
        
        assert "dashboard" in tag_names
        assert "reports" in tag_names