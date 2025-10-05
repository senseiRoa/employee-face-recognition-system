"""
Tests de autenticación y autorización por roles
Utiliza configuración unificada de conftest.py
"""

import pytest
from .conftest import client, get_auth_token


class TestAuthentication:
    """Tests básicos de autenticación"""

    def test_login_success_admin(self, setup_test_data):
        """Test: Admin puede hacer login"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "admin_test", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_success_manager(self, setup_test_data):
        """Test: Manager puede hacer login"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "manager_test", "password": "manager123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_success_employee(self, setup_test_data):
        """Test: Employee puede hacer login"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "employee_test", "password": "employee123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "employee"

    def test_login_with_email(self, setup_test_data):
        """Test: Login con email funciona"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "admin@test.com", "password": "admin123"},
        )
        assert response.status_code == 200

    def test_login_invalid_credentials(self, setup_test_data):
        """Test: Credenciales inválidas fallan"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "admin_test", "password": "wrong_password"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, setup_test_data):
        """Test: Usuario inexistente falla"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "nonexistent", "password": "password"},
        )
        assert response.status_code == 401


import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models import User, Role, Company
from utils.password import hash_password

# Configuración de base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
def setup_database():
    """Configurar base de datos de prueba"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Crear roles
    roles_data = [
        {"id": 1, "name": "admin", "description": "Administrator"},
        {"id": 2, "name": "manager", "description": "Manager"},
        {"id": 3, "name": "employee", "description": "Employee"},
    ]

    for role_data in roles_data:
        role = Role(**role_data)
        db.add(role)

    # Crear compañía de prueba
    company = Company(id=1, name="Test Company", email="test@company.com")
    db.add(company)

    # Crear usuarios de prueba con diferentes roles
    users = [
        User(
            id=1,
            username="admin_test",
            email="admin@test.com",
            password=hash_password("admin123"),
            company_id=1,
            role_id=1,
            is_active=True,
            first_name="Admin",
            last_name="Test",
        ),
        User(
            id=2,
            username="manager_test",
            email="manager@test.com",
            password=hash_password("manager123"),
            company_id=1,
            role_id=2,
            is_active=True,
            first_name="Manager",
            last_name="Test",
        ),
        User(
            id=3,
            username="employee_test",
            email="employee@test.com",
            password=hash_password("employee123"),
            company_id=1,
            role_id=3,
            is_active=True,
            first_name="Employee",
            last_name="Test",
        ),
    ]

    for user in users:
        db.add(user)

    db.commit()
    db.close()

    yield

    # Limpiar después de las pruebas
    Base.metadata.drop_all(bind=engine)


def get_auth_token(username: str, password: str) -> str:
    """Helper para obtener token de autenticación"""
    response = client.post(
        "/auth/login", json={"username_or_email": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestAuthentication:
    """Tests de autenticación básica"""

    def test_login_success_admin(self, setup_database):
        """Test: Admin puede hacer login"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "admin_test", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_success_manager(self, setup_database):
        """Test: Manager puede hacer login"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "manager_test", "password": "manager123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_success_employee(self, setup_database):
        """Test: Employee puede hacer login"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "employee_test", "password": "employee123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "employee"

    def test_login_with_email(self, setup_database):
        """Test: Login con email funciona"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "admin@test.com", "password": "admin123"},
        )
        assert response.status_code == 200

    def test_login_invalid_credentials(self, setup_database):
        """Test: Credenciales inválidas fallan"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "admin_user", "password": "wrong_password"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, setup_database):
        """Test: Usuario inexistente falla"""
        response = client.post(
            "/auth/login",
            json={"username_or_email": "nonexistent", "password": "password"},
        )
        assert response.status_code == 401


class TestAuthEndpoints:
    """Tests de endpoints de autenticación"""

    def test_auth_me_admin(self, setup_database):
        """Test: Admin puede ver su propia información"""
        token = get_auth_token("admin_user", "admin123")
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin_user"
        assert data["role"] == "admin"

    def test_auth_me_without_token(self, setup_database):
        """Test: Endpoint /auth/me requiere autenticación"""
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestUserRegistration:
    """Tests de registro de usuarios por rol"""

    def test_admin_can_create_any_user(self, setup_database):
        """Test: Admin puede crear cualquier tipo de usuario"""
        token = get_auth_token("admin_user", "admin123")

        # Admin crea un manager
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "new_manager",
                "email": "newmanager@test.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "Manager",
                "role_id": 2,
            },
        )
        assert response.status_code == 201
        assert "User created successfully" in response.json()["message"]

    def test_admin_can_create_admin(self, setup_database):
        """Test: Admin puede crear otro admin"""
        token = get_auth_token("admin_user", "admin123")

        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "new_admin",
                "email": "newadmin@test.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "Admin",
                "role_id": 1,
            },
        )
        assert response.status_code == 201

    def test_manager_can_create_employee(self, setup_database):
        """Test: Manager puede crear empleados"""
        token = get_auth_token("manager_user", "manager123")

        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "new_employee",
                "email": "newemployee@test.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "Employee",
                "role_id": 3,
            },
        )
        assert response.status_code == 201

    def test_manager_cannot_create_admin(self, setup_database):
        """Test: Manager NO puede crear admins"""
        token = get_auth_token("manager_user", "manager123")

        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "fake_admin",
                "email": "fakeadmin@test.com",
                "password": "newpass123",
                "first_name": "Fake",
                "last_name": "Admin",
                "role_id": 1,
            },
        )
        assert response.status_code == 403
        assert "Managers cannot create admin users" in response.json()["detail"]

    def test_employee_cannot_create_users(self, setup_database):
        """Test: Employee NO puede crear usuarios"""
        token = get_auth_token("employee_user", "employee123")

        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "unauthorized",
                "email": "unauthorized@test.com",
                "password": "newpass123",
                "first_name": "Unauthorized",
                "last_name": "User",
            },
        )
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_unauthenticated_cannot_register(self, setup_database):
        """Test: Usuario no autenticado NO puede registrar"""
        response = client.post(
            "/auth/register",
            json={
                "username": "unauthorized",
                "email": "unauthorized@test.com",
                "password": "newpass123",
            },
        )
        assert response.status_code == 401


class TestUserManagement:
    """Tests de gestión de usuarios"""

    def test_admin_can_list_all_users(self, setup_database):
        """Test: Admin puede ver todos los usuarios"""
        token = get_auth_token("admin_user", "admin123")
        response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 3  # Al menos admin, manager, employee

    def test_manager_can_list_company_users(self, setup_database):
        """Test: Manager puede ver usuarios de su compañía"""
        token = get_auth_token("manager_user", "manager123")
        response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        users = response.json()
        # Todos los usuarios deben ser de la misma compañía
        for user in users:
            assert user["company_id"] == 1

    def test_employee_cannot_list_users(self, setup_database):
        """Test: Employee NO puede listar usuarios"""
        token = get_auth_token("employee_user", "employee123")
        response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_user_can_view_own_profile(self, setup_database):
        """Test: Usuario puede ver su propio perfil"""
        token = get_auth_token("employee_user", "employee123")
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "employee_user"


class TestCompanyManagement:
    """Tests de gestión de compañías"""

    def test_user_can_view_own_company(self, setup_database):
        """Test: Usuario puede ver información de su compañía"""
        token = get_auth_token("admin_user", "admin123")
        response = client.get(
            "/companies/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Company"

    def test_admin_can_list_all_companies(self, setup_database):
        """Test: Admin puede listar todas las compañías"""
        token = get_auth_token("admin_user", "admin123")
        response = client.get(
            "/companies/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) >= 1

    def test_non_admin_cannot_list_all_companies(self, setup_database):
        """Test: No-admin NO puede listar todas las compañías"""
        token = get_auth_token("manager_user", "manager123")
        response = client.get(
            "/companies/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


class TestEdgeCases:
    """Tests de casos edge y seguridad"""

    def test_invalid_token(self, setup_database):
        """Test: Token inválido es rechazado"""
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_expired_token_handling(self, setup_database):
        """Test: Manejo de tokens (simulación)"""
        # Este test requeriría mockear la expiración de tokens
        # Por ahora verificamos que el sistema maneja errores de token
        response = client.get("/users/me", headers={"Authorization": "Bearer "})
        assert response.status_code == 401

    def test_duplicate_username_registration(self, setup_database):
        """Test: No se puede registrar username duplicado"""
        token = get_auth_token("admin_user", "admin123")

        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "admin_user",  # Username ya existe
                "email": "different@test.com",
                "password": "newpass123",
                "first_name": "Duplicate",
                "last_name": "User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_duplicate_email_registration(self, setup_database):
        """Test: No se puede registrar email duplicado"""
        token = get_auth_token("admin_user", "admin123")

        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "different_user",
                "email": "admin@test.com",  # Email ya existe
                "password": "newpass123",
                "first_name": "Duplicate",
                "last_name": "Email",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
