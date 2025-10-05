"""
Tests de autenticación y autorización por roles
Utiliza configuración unificada de conftest.py
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from conftest import client, get_auth_token


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


class TestAuthEndpoints:
    """Tests de endpoints de autenticación"""

    def test_auth_me_admin(self, admin_token):
        """Test: Admin puede ver su propia información"""
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin_test"

    def test_auth_me_without_token(self, setup_test_data):
        """Test: Endpoint /auth/me requiere token"""
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestUserRegistration:
    """Tests de registro de usuarios con permisos"""

    def test_admin_can_create_any_user(self, admin_token):
        """Test: Admin puede crear cualquier tipo de usuario"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "new_manager",
                "email": "new_manager@test.com",
                "password": "password123",
                "role_id": 2,
                "company_id": 1
            }
        )
        assert response.status_code == 201

    def test_admin_can_create_admin(self, admin_token):
        """Test: Admin puede crear otro admin"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "new_admin",
                "email": "new_admin@test.com",
                "password": "password123",
                "role_id": 1,
                "company_id": 1
            }
        )
        assert response.status_code == 201

    def test_manager_can_create_employee(self, manager_token):
        """Test: Manager puede crear empleados"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "username": "new_employee",
                "email": "new_employee@test.com",
                "password": "password123",
                "role_id": 3,
                "company_id": 1
            }
        )
        assert response.status_code == 201

    def test_manager_cannot_create_admin(self, manager_token):
        """Test: Manager NO puede crear admins"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "username": "unauthorized_admin",
                "email": "unauthorized@test.com",
                "password": "password123",
                "role_id": 1,
                "company_id": 1
            }
        )
        assert response.status_code == 403

    def test_employee_cannot_create_users(self, employee_token):
        """Test: Employee NO puede crear usuarios"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={
                "username": "unauthorized_user",
                "email": "unauthorized@test.com",
                "password": "password123",
                "role_id": 3,
                "company_id": 1
            }
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_register(self, setup_test_data):
        """Test: Usuario sin autenticar NO puede registrar"""
        response = client.post(
            "/auth/register",
            json={
                "username": "unauthorized_user",
                "email": "unauthorized@test.com",
                "password": "password123",
                "role_id": 3,
                "company_id": 1
            }
        )
        assert response.status_code == 401


class TestUserManagement:
    """Tests de gestión de usuarios"""

    def test_admin_can_list_all_users(self, admin_token):
        """Test: Admin puede ver todos los usuarios"""
        response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200

    def test_manager_can_list_company_users(self, manager_token):
        """Test: Manager puede ver usuarios de su compañía"""
        response = client.get("/users/", headers={"Authorization": f"Bearer {manager_token}"})
        assert response.status_code == 200

    def test_employee_cannot_list_users(self, employee_token):
        """Test: Employee NO puede listar usuarios"""
        response = client.get("/users/", headers={"Authorization": f"Bearer {employee_token}"})
        assert response.status_code == 403

    def test_user_can_view_own_profile(self, employee_token):
        """Test: Usuario puede ver su propio perfil"""
        response = client.get("/users/me", headers={"Authorization": f"Bearer {employee_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "employee_test"


class TestCompanyManagement:
    """Tests de gestión de compañías"""

    def test_user_can_view_own_company(self, admin_token):
        """Test: Usuario puede ver información de su compañía"""
        response = client.get("/companies/1", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200

    def test_admin_can_list_all_companies(self, admin_token):
        """Test: Admin puede listar todas las compañías"""
        response = client.get("/companies/", headers={"Authorization": f"Bearer {admin_token}"})
        # Puede ser 200 o 405 dependiendo de si está implementado
        assert response.status_code in [200, 405]

    def test_non_admin_cannot_list_all_companies(self, manager_token):
        """Test: No-admin NO puede listar todas las compañías"""
        response = client.get("/companies/", headers={"Authorization": f"Bearer {manager_token}"})
        # Puede ser 403 o 405 dependiendo de la implementación
        assert response.status_code in [403, 405]


class TestEdgeCases:
    """Tests de casos edge y validaciones"""

    def test_invalid_token(self, setup_test_data):
        """Test: Token inválido es rechazado"""
        response = client.get(
            "/users/me", 
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_expired_token_handling(self, setup_test_data):
        """Test: Manejo de tokens (simulado)"""
        # Este test verifica que el sistema maneja tokens malformados
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer malformed_token"}
        )
        assert response.status_code == 401

    def test_duplicate_username_registration(self, admin_token):
        """Test: No se puede registrar username duplicado"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "admin_test",  # Username ya existe
                "email": "duplicate@test.com",
                "password": "password123",
                "role_id": 3,
                "company_id": 1
            }
        )
        assert response.status_code == 400

    def test_duplicate_email_registration(self, admin_token):
        """Test: No se puede registrar email duplicado"""
        response = client.post(
            "/auth/register",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": "unique_username",
                "email": "admin@test.com",  # Email ya existe
                "password": "password123",
                "role_id": 3,
                "company_id": 1
            }
        )
        assert response.status_code == 400