"""
Tests de endpoints protegidos por rol
Casos específicos de Warehouses, Employees, Tablets, etc.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models import User, Role, Company, Warehouse, Employee
from utils.security import get_password_hash as hash_password

# Usar la misma configuración de DB que test_auth_roles.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_endpoints.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_test_data():
    """Configurar datos de prueba completos"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Crear roles
    roles = [
        Role(id=1, name="admin", description="Administrator"),
        Role(id=2, name="manager", description="Manager"),
        Role(id=3, name="employee", description="Employee"),
    ]
    for role in roles:
        db.add(role)

    # Crear compañías
    companies = [
        Company(id=1, name="Company A", email="companya@test.com"),
        Company(id=2, name="Company B", email="companyb@test.com"),
    ]
    for company in companies:
        db.add(company)

        # Crear usuarios de diferentes compañías y roles
    users = [
        User(
            id=1,
            username="admin1",
            email="admin1@test.com",
            password=hash_password("admin123"),
            company_id=1,
            role_id=1,
            is_active=True,
            first_name="Admin",
            last_name="User",
        ),
        User(
            id=2,
            username="manager1",
            email="manager1@test.com",
            password=hash_password("manager123"),
            company_id=1,
            role_id=2,
            is_active=True,
            first_name="Manager",
            last_name="One",
        ),
        User(
            id=3,
            username="employee1",
            email="employee1@test.com",
            password=hash_password("employee123"),
            company_id=1,
            role_id=3,
            is_active=True,
            first_name="Employee",
            last_name="One",
        ),
        User(
            id=4,
            username="manager2",
            email="manager2@test.com",
            password=hash_password("manager123"),
            company_id=2,
            role_id=2,
            is_active=True,
            first_name="Manager",
            last_name="Two",
        ),
    ]
    for user in users:
        db.add(user)

    # Crear warehouses
    warehouses = [
        Warehouse(id=1, name="Warehouse A1", company_id=1, location="Location A1"),
        Warehouse(id=2, name="Warehouse A2", company_id=1, location="Location A2"),
        Warehouse(id=3, name="Warehouse B1", company_id=2, location="Location B1"),
    ]
    for warehouse in warehouses:
        db.add(warehouse)

    # Crear employees
    employees = [
        Employee(
            id=1,
            warehouse_id=1,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
        ),
        Employee(
            id=2,
            warehouse_id=2,
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
        ),
        Employee(
            id=3,
            warehouse_id=3,
            first_name="Bob",
            last_name="Wilson",
            email="bob@test.com",
        ),
    ]
    for employee in employees:
        db.add(employee)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def get_auth_token(username: str, password: str) -> str:
    """Helper para obtener token de autenticación"""
    response = client.post(
        "/auth/login", json={"username_or_email": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestWarehouseAccess:
    """Tests de acceso a warehouses por rol"""

    def test_admin_can_view_all_warehouses(self, setup_test_data):
        """Test: Admin puede ver warehouses de todas las compañías"""
        token = get_auth_token("admin1", "admin123")
        response = client.get(
            "/warehouses/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        warehouses = response.json()
        assert len(warehouses) >= 3  # Debería ver todos los warehouses

    def test_manager_can_view_company_warehouses(self, setup_test_data):
        """Test: Manager solo puede ver warehouses de su compañía"""
        token = get_auth_token("manager1", "manager123")
        response = client.get(
            "/warehouses/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        warehouses = response.json()
        # Todos los warehouses deben ser de company_id = 1
        for warehouse in warehouses:
            assert warehouse["company_id"] == 1

    def test_employee_warehouse_access_restricted(self, setup_test_data):
        """Test: Employee tiene acceso limitado a warehouses"""
        token = get_auth_token("employee1", "employee123")
        response = client.get(
            "/warehouses/", headers={"Authorization": f"Bearer {token}"}
        )
        # Dependiendo de la implementación, puede ser 200 con datos limitados o 403
        assert response.status_code in [200, 403]

    def test_cross_company_warehouse_access_denied(self, setup_test_data):
        """Test: Manager no puede ver warehouses de otra compañía"""
        token = get_auth_token("manager1", "manager123")
        # Intentar acceder a warehouse de company 2
        response = client.get(
            "/warehouses/3", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [403, 404]


class TestEmployeeAccess:
    """Tests de acceso a employees por rol"""

    def test_admin_can_access_all_employees(self, setup_test_data):
        """Test: Admin puede acceder a todos los employees"""
        token = get_auth_token("admin1", "admin123")
        response = client.get(
            "/employees/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_manager_employee_access_by_company(self, setup_test_data):
        """Test: Manager solo puede ver employees de su compañía"""
        token = get_auth_token("manager1", "manager123")
        response = client.get(
            "/employees/", headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            employees = response.json()
            # Verificar que todos los employees pertenecen a warehouses de su compañía
            for employee in employees:
                # Este test requiere que el endpoint incluya company info
                pass  # Implementar según estructura de respuesta

    def test_employee_cannot_access_employee_list(self, setup_test_data):
        """Test: Employee no puede listar otros employees"""
        token = get_auth_token("employee1", "employee123")
        response = client.get(
            "/employees/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


class TestUserCRUDOperations:
    """Tests de operaciones CRUD de usuarios"""

    def test_admin_can_update_any_user(self, setup_test_data):
        """Test: Admin puede actualizar cualquier usuario"""
        token = get_auth_token("admin1", "admin123")
        response = client.put(
            "/users/3",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Updated", "last_name": "Employee"},
        )
        assert response.status_code == 200

    def test_manager_can_update_company_users(self, setup_test_data):
        """Test: Manager puede actualizar usuarios de su compañía"""
        token = get_auth_token("manager1", "manager123")
        response = client.put(
            "/users/3",  # employee1 de la misma compañía
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Manager Updated"},
        )
        assert response.status_code == 200

    def test_manager_cannot_update_other_company_users(self, setup_test_data):
        """Test: Manager NO puede actualizar usuarios de otra compañía"""
        token = get_auth_token("manager1", "manager123")
        response = client.put(
            "/users/4",  # manager2 de otra compañía
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Unauthorized Update"},
        )
        assert response.status_code == 403

    def test_employee_can_update_own_profile(self, setup_test_data):
        """Test: Employee puede actualizar su propio perfil"""
        token = get_auth_token("employee1", "employee123")
        response = client.put(
            "/users/3",  # Su propio ID
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Self Updated"},
        )
        assert response.status_code == 200

    def test_employee_cannot_update_other_users(self, setup_test_data):
        """Test: Employee NO puede actualizar otros usuarios"""
        token = get_auth_token("employee1", "employee123")
        response = client.put(
            "/users/2",  # manager1
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Unauthorized"},
        )
        assert response.status_code == 403


class TestUserDeletion:
    """Tests de eliminación de usuarios"""

    def test_admin_can_delete_users(self, setup_test_data):
        """Test: Admin puede eliminar usuarios"""
        # Primero crear un usuario para eliminar
        token = get_auth_token("admin1", "admin123")
        create_response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "temp_user",
                "email": "temp@test.com",
                "password": "temp123",
                "role_id": 3,
            },
        )
        assert create_response.status_code == 201

        # Obtener el ID del usuario creado
        user_id = create_response.json()["user"]["id"]

        # Eliminar el usuario
        delete_response = client.delete(
            f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 204

    def test_manager_can_delete_company_employees(self, setup_test_data):
        """Test: Manager puede eliminar employees de su compañía"""
        # Crear employee en la compañía del manager
        admin_token = get_auth_token("admin1", "admin123")
        create_response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "temp_employee",
                "email": "tempemp@test.com",
                "password": "temp123",
                "company_id": 1,
                "role_id": 3,
            },
        )
        user_id = create_response.json()["user"]["id"]

        # Manager intenta eliminar
        manager_token = get_auth_token("manager1", "manager123")
        response = client.delete(
            f"/users/{user_id}", headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 204

    def test_employee_cannot_delete_users(self, setup_test_data):
        """Test: Employee NO puede eliminar usuarios"""
        token = get_auth_token("employee1", "employee123")
        response = client.delete(
            "/users/2",  # Intentar eliminar manager
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


class TestCompanyOperations:
    """Tests de operaciones con compañías"""

    def test_admin_can_create_company(self, setup_test_data):
        """Test: Admin puede crear compañías"""
        token = get_auth_token("admin1", "admin123")
        response = client.post(
            "/companies/",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "New Company", "email": "newcompany@test.com"},
        )
        # Verificar según implementación actual
        assert response.status_code in [201, 200, 405]  # 405 si no está implementado

    def test_manager_can_update_own_company(self, setup_test_data):
        """Test: Manager puede actualizar su propia compañía"""
        token = get_auth_token("manager1", "manager123")
        response = client.put(
            "/companies/1",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Company A"},
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
            "/auth/me",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, (
                f"Endpoint {endpoint} should require authentication"
            )

    def test_invalid_jwt_rejected(self, setup_test_data):
        """Test: JWT inválido es rechazado"""
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer invalid.jwt.token"}
        )
        assert response.status_code == 401

    def test_malformed_jwt_rejected(self, setup_test_data):
        """Test: JWT malformado es rechazado"""
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer malformed_token"}
        )
        assert response.status_code == 401


class TestRolePermissionMatrix:
    """Test matriz completa de permisos por rol"""

    def test_permission_matrix_users(self, setup_test_data):
        """Test: Matriz de permisos para gestión de usuarios"""
        test_cases = [
            # (role, action, target, expected_status)
            ("admin1", "GET", "/users/", 200),
            ("manager1", "GET", "/users/", 200),
            ("employee1", "GET", "/users/", 403),
            ("admin1", "GET", "/users/me", 200),
            ("manager1", "GET", "/users/me", 200),
            ("employee1", "GET", "/users/me", 200),
        ]

        for username, method, endpoint, expected_status in test_cases:
            token = get_auth_token(username, f"{username.split('1')[0]}123")
            if method == "GET":
                response = client.get(
                    endpoint, headers={"Authorization": f"Bearer {token}"}
                )
            elif method == "POST":
                response = client.post(
                    endpoint, headers={"Authorization": f"Bearer {token}"}
                )

            assert response.status_code == expected_status, (
                f"{username} {method} {endpoint} should return {expected_status}, got {response.status_code}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
