"""
Configuración común para todos los tests
Fixtures compartidas y configuración de base de datos unificada
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from models import User, Role, Company, Warehouse, Employee
from utils.password import hash_password

# Configuración unificada de base de datos de prueba
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_unified.db"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override de la función get_db para usar base de datos de prueba"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="session")
def test_db():
    """Fixture de base de datos para toda la sesión de tests"""
    # Crear todas las tablas
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Limpiar al final de la sesión
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Fixture de sesión de base de datos para cada test"""
    connection = test_db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def setup_test_data(db_session):
    """Fixture para datos de prueba estándar"""
    # Crear roles
    roles_data = [
        Role(id=1, name="admin", description="Administrator"),
        Role(id=2, name="manager", description="Manager"),
        Role(id=3, name="employee", description="Employee"),
    ]
    for role in roles_data:
        db_session.add(role)

    # Crear compañías
    companies = [
        Company(id=1, name="Test Company A", email="companya@test.com"),
        Company(id=2, name="Test Company B", email="companyb@test.com")
    ]
    for company in companies:
        db_session.add(company)

    # Crear usuarios de prueba con diferentes roles
    users = [
        User(id=1, username="admin_test", email="admin@test.com",
             password=hash_password("admin123"), company_id=1, role_id=1, is_active=True,
             first_name="Admin", last_name="Test"),
        User(id=2, username="manager_test", email="manager@test.com",
             password=hash_password("manager123"), company_id=1, role_id=2, is_active=True,
             first_name="Manager", last_name="Test"),
        User(id=3, username="employee_test", email="employee@test.com",
             password=hash_password("employee123"), company_id=1, role_id=3, is_active=True,
             first_name="Employee", last_name="Test"),
        User(id=4, username="manager2_test", email="manager2@test.com",
             password=hash_password("manager123"), company_id=2, role_id=2, is_active=True,
             first_name="Manager2", last_name="Test"),
    ]
    for user in users:
        db_session.add(user)

    # Crear warehouses
    warehouses = [
        Warehouse(id=1, name="Warehouse A1", company_id=1, location="Location A1"),
        Warehouse(id=2, name="Warehouse A2", company_id=1, location="Location A2"),
        Warehouse(id=3, name="Warehouse B1", company_id=2, location="Location B1"),
    ]
    for warehouse in warehouses:
        db_session.add(warehouse)

    # Crear employees
    employees = [
        Employee(id=1, warehouse_id=1, first_name="John", last_name="Doe", email="john@test.com"),
        Employee(id=2, warehouse_id=2, first_name="Jane", last_name="Smith", email="jane@test.com"),
        Employee(id=3, warehouse_id=3, first_name="Bob", last_name="Wilson", email="bob@test.com"),
    ]
    for employee in employees:
        db_session.add(employee)

    db_session.commit()
    return {
        "users": users,
        "companies": companies,
        "warehouses": warehouses,
        "employees": employees,
        "roles": roles_data
    }


def get_auth_token(username: str, password: str) -> str:
    """Helper para obtener token de autenticación"""
    response = client.post("/auth/login", json={
        "username_or_email": username,
        "password": password
    })
    assert response.status_code == 200, f"Login failed for {username}: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_token(setup_test_data):
    """Token de admin para tests"""
    return get_auth_token("admin_test", "admin123")


@pytest.fixture
def manager_token(setup_test_data):
    """Token de manager para tests"""
    return get_auth_token("manager_test", "manager123")


@pytest.fixture
def employee_token(setup_test_data):
    """Token de employee para tests"""
    return get_auth_token("employee_test", "employee123")


@pytest.fixture
def test_client():
    """Cliente de pruebas FastAPI"""
    return client