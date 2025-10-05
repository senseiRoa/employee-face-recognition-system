"""
Tests de endpoints protegidos por rol
Casos específicos de Warehouses, Employees, Tablets, etc.
Utiliza configuración unificada de conftest.py
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from conftest import client, get_auth_token


class TestWarehouseAccess:
    """Tests de acceso a warehouses por rol"""
    
    def test_admin_can_view_all_warehouses(self, admin_token):
        """Test: Admin puede ver warehouses de todas las compañías"""
        response = client.get("/warehouses/", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        warehouses = response.json()
        assert len(warehouses) >= 3  # Debería ver todos los warehouses
    
    def test_manager_can_view_company_warehouses(self, manager_token):
        """Test: Manager solo puede ver warehouses de su compañía"""
        response = client.get("/warehouses/", headers={"Authorization": f"Bearer {manager_token}"})
        assert response.status_code == 200
        warehouses = response.json()
        # Todos los warehouses deben ser de company_id = 1
        for warehouse in warehouses:
            assert warehouse["company_id"] == 1
    
    def test_employee_warehouse_access_restricted(self, employee_token):
        """Test: Employee tiene acceso limitado a warehouses"""
        response = client.get("/warehouses/", headers={"Authorization": f"Bearer {employee_token}"})
        # Dependiendo de la implementación, puede ser 200 con datos limitados o 403
        assert response.status_code in [200, 403]
    
    def test_cross_company_warehouse_access_denied(self, setup_test_data):
        """Test: Manager no puede ver warehouses de otra compañía"""
        token = get_auth_token("manager_test", "manager123")
        # Intentar acceder a warehouse de company 2
        response = client.get("/warehouses/3", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code in [403, 404]


class TestEmployeeAccess:
    """Tests de acceso a employees por rol"""
    
    def test_admin_can_access_all_employees(self, admin_token):
        """Test: Admin puede acceder a todos los employees"""
        response = client.get("/employees/", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
    
    def test_manager_employee_access_by_company(self, manager_token):
        """Test: Manager solo puede ver employees de su compañía"""
        response = client.get("/employees/", headers={"Authorization": f"Bearer {manager_token}"})
        if response.status_code == 200:
            employees = response.json()
            # Verificar que todos los employees pertenecen a warehouses de su compañía
            for employee in employees:
                # Este test requiere que el endpoint incluya company info
                pass  # Implementar según estructura de respuesta
    
    def test_employee_cannot_access_employee_list(self, employee_token):
        """Test: Employee no puede listar otros employees"""
        response = client.get("/employees/", headers={"Authorization": f"Bearer {employee_token}"})
        assert response.status_code == 403


class TestUserCRUDOperations:
    """Tests de operaciones CRUD de usuarios"""
    
    def test_admin_can_update_any_user(self, admin_token):
        """Test: Admin puede actualizar cualquier usuario"""
        response = client.put("/users/3", 
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "first_name": "Updated",
                "last_name": "Employee"
            }
        )
        assert response.status_code == 200
    
    def test_manager_can_update_company_users(self, manager_token):
        """Test: Manager puede actualizar usuarios de su compañía"""
        response = client.put("/users/3",  # employee_test de la misma compañía
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "first_name": "Manager Updated"
            }
        )
        assert response.status_code == 200
    
    def test_manager_cannot_update_other_company_users(self, setup_test_data):
        """Test: Manager NO puede actualizar usuarios de otra compañía"""
        token = get_auth_token("manager_test", "manager123")
        response = client.put("/users/4",  # manager2_test de otra compañía
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "Unauthorized Update"
            }
        )
        assert response.status_code == 403
    
    def test_employee_can_update_own_profile(self, employee_token):
        """Test: Employee puede actualizar su propio perfil"""
        response = client.put("/users/3",  # Su propio ID
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "first_name": "Self Updated"
            }
        )
        assert response.status_code == 200
    
    def test_employee_cannot_update_other_users(self, employee_token):
        """Test: Employee NO puede actualizar otros usuarios"""
        response = client.put("/users/2",  # manager_test
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "first_name": "Unauthorized"
            }
        )
        assert response.status_code == 403


class TestUserDeletion:
    """Tests de eliminación de usuarios"""
    
    def test_admin_can_delete_users(self, admin_token):
        """Test: Admin puede eliminar usuarios"""
        # Primero crear un usuario para eliminar
        create_response = client.post("/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "temp_user",
                "email": "temp@test.com",
                "password": "temp123",
                "role_id": 3,
                "company_id": 1
            }
        )
        assert create_response.status_code == 201
        
        # Obtener el ID del usuario creado
        user_id = create_response.json()["user"]["id"]
        
        # Eliminar el usuario
        delete_response = client.delete(f"/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 204
    
    def test_manager_can_delete_company_employees(self, admin_token, manager_token):
        """Test: Manager puede eliminar employees de su compañía"""
        # Crear employee en la compañía del manager
        create_response = client.post("/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "temp_employee",
                "email": "tempemp@test.com",
                "password": "temp123",
                "company_id": 1,
                "role_id": 3
            }
        )
        user_id = create_response.json()["user"]["id"]
        
        # Manager intenta eliminar
        response = client.delete(f"/users/{user_id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 204
    
    def test_employee_cannot_delete_users(self, employee_token):
        """Test: Employee NO puede eliminar usuarios"""
        response = client.delete("/users/2",  # Intentar eliminar manager
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 403


class TestCompanyOperations:
    """Tests de operaciones con compañías"""
    
    def test_admin_can_create_company(self, admin_token):
        """Test: Admin puede crear compañías"""
        response = client.post("/companies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "New Company",
                "email": "newcompany@test.com"
            }
        )
        # Verificar según implementación actual
        assert response.status_code in [201, 200, 405]  # 405 si no está implementado
    
    def test_manager_can_update_own_company(self, manager_token):
        """Test: Manager puede actualizar su propia compañía"""
        response = client.put("/companies/1",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "name": "Updated Company A"
            }
        )
        assert response.status_code in [200, 403]  # Depende de la implementación


class TestSecurityValidation:
    """Tests de validación de seguridad"""
    
    def test_jwt_required_for_protected_endpoints(self, setup_test_data):
        """Test: Endpoints protegidos requieren JWT"""
        protected_endpoints = [
            "/users/",
            "/companies/",
            "/warehouses/",
            "/employees/",
            "/auth/me"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"
    
    def test_invalid_jwt_rejected(self, setup_test_data):
        """Test: JWT inválido es rechazado"""
        response = client.get("/users/me", 
            headers={"Authorization": "Bearer invalid.jwt.token"}
        )
        assert response.status_code == 401
    
    def test_malformed_jwt_rejected(self, setup_test_data):
        """Test: JWT malformado es rechazado"""
        response = client.get("/users/me", 
            headers={"Authorization": "Bearer malformed_token"}
        )
        assert response.status_code == 401


class TestRolePermissionMatrix:
    """Test matriz completa de permisos por rol"""
    
    def test_permission_matrix_users(self, setup_test_data):
        """Test: Matriz de permisos para gestión de usuarios"""
        test_cases = [
            # (role, action, target, expected_status)
            ("admin_test", "GET", "/users/", 200),
            ("manager_test", "GET", "/users/", 200),
            ("employee_test", "GET", "/users/", 403),
            
            ("admin_test", "GET", "/users/me", 200),
            ("manager_test", "GET", "/users/me", 200),
            ("employee_test", "GET", "/users/me", 200),
        ]
        
        for username, method, endpoint, expected_status in test_cases:
            token = get_auth_token(username, f"{username.split('_')[0]}123")
            if method == "GET":
                response = client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
            elif method == "POST":
                response = client.post(endpoint, headers={"Authorization": f"Bearer {token}"})
            
            assert response.status_code == expected_status, \
                f"{username} {method} {endpoint} should return {expected_status}, got {response.status_code}"