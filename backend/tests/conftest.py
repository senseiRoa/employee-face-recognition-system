"""
Common configuration for all tests
Shared fixtures and unified database configuration
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

# Strong passwords for tests
TEST_PASSWORDS = {
    "admin": "SystemHead2024!",
    "manager": "OfficeChief2024#",
    "employee": "StaffMember2024$",
    "temp": "TempAccess123!",
}

# Unified test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_unified.db"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override get_db function to use test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="session")
def test_db():
    """Database fixture for the entire test session"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Clean up at the end of the session
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Database session fixture for each test"""
    connection = test_db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def setup_test_data(db_session):
    """Fixture for standard test data with warehouse-based architecture"""
    # Create roles with warehouse-based permissions
    roles_data = [
        Role(
            id=1,
            name="admin",
            description="Administrator",
            permissions={
                "can_manage_users": True,
                "can_manage_employees": True,
                "can_view_reports": True,
            },
            scope="warehouse",
        ),
        Role(
            id=2,
            name="manager",
            description="Manager",
            permissions={
                "can_manage_employees": True,
                "can_view_reports": True,
                "can_manage_access": True,
            },
            scope="warehouse",
        ),
        Role(
            id=3,
            name="employee",
            description="Employee",
            permissions={"can_clock_in": True, "can_view_own_logs": True},
            scope="warehouse",
        ),
    ]
    for role in roles_data:
        db_session.add(role)

    # Create companies
    companies = [
        Company(id=1, name="Test Company A", email="companya@test.com"),
        Company(id=2, name="Test Company B", email="companyb@test.com"),
    ]
    for company in companies:
        db_session.add(company)

    # Create warehouses
    warehouses = [
        Warehouse(
            id=1,
            company_id=1,
            name="Main Warehouse A",
            location="Location A",
            timezone="America/New_York",
            is_active=True,
        ),
        Warehouse(
            id=2,
            company_id=1,
            name="Secondary Warehouse A",
            location="Location A2",
            timezone="America/New_York",
            is_active=True,
        ),
        Warehouse(
            id=3,
            company_id=2,
            name="Main Warehouse B",
            location="Location B",
            timezone="America/Chicago",
            is_active=True,
        ),
    ]
    for warehouse in warehouses:
        db_session.add(warehouse)

    # Create test users with different roles (now with warehouse_id instead of company_id)
    users = [
        User(
            id=1,
            username="admin_test",
            email="admin@test.com",
            password=hash_password(TEST_PASSWORDS["admin"]),
            warehouse_id=1,
            role_id=1,
            is_active=True,
            first_name="Admin",
            last_name="Test",
        ),
        User(
            id=2,
            username="manager_test",
            email="manager@test.com",
            password=hash_password(TEST_PASSWORDS["manager"]),
            warehouse_id=1,
            role_id=2,
            is_active=True,
            first_name="Manager",
            last_name="Test",
        ),
        User(
            id=3,
            username="employee_test",
            email="employee@test.com",
            password=hash_password(TEST_PASSWORDS["employee"]),
            warehouse_id=1,
            role_id=3,
            is_active=True,
            first_name="Employee",
            last_name="Test",
        ),
        User(
            id=4,
            username="manager2_test",
            email="manager2@test.com",
            password=hash_password(TEST_PASSWORDS["manager"]),
            warehouse_id=2,  # Different warehouse
            role_id=2,
            is_active=True,
            first_name="Manager2",
            last_name="Test",
        ),
        User(
            id=5,
            username="manager3_test",
            email="manager3@test.com",
            password=hash_password(TEST_PASSWORDS["manager"]),
            warehouse_id=3,  # Different company's warehouse
            role_id=2,
            is_active=True,
            first_name="Manager3",
            last_name="Test",
        ),
    ]
    for user in users:
        db_session.add(user)

    # Create employees
    employees = [
        Employee(
            id=1,
            warehouse_id=1,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            employee_code="EMP001",
            department="Operations",
            position="Operator",
            is_active=True,
        ),
        Employee(
            id=2,
            warehouse_id=2,
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            employee_code="EMP002",
            department="Quality",
            position="Inspector",
            is_active=True,
        ),
        Employee(
            id=3,
            warehouse_id=3,
            first_name="Bob",
            last_name="Wilson",
            email="bob@test.com",
            employee_code="EMP003",
            department="Logistics",
            position="Coordinator",
            is_active=True,
        ),
    ]
    for employee in employees:
        db_session.add(employee)

    db_session.commit()
    return {
        "users": users,
        "companies": companies,
        "warehouses": warehouses,
        "employees": employees,
        "roles": roles_data,
    }


def get_auth_token(username: str, password: str) -> str:
    """Helper para obtener token de autenticación"""
    response = client.post(
        "/auth/login", json={"username_or_email": username, "password": password}
    )
    assert response.status_code == 200, f"Login failed for {username}: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_token(setup_test_data):
    """Token de admin para tests"""
    return get_auth_token("admin_test", TEST_PASSWORDS["admin"])


@pytest.fixture
def manager_token(setup_test_data):
    """Token de manager para tests"""
    return get_auth_token("manager_test", TEST_PASSWORDS["manager"])


@pytest.fixture
def employee_token(setup_test_data):
    """Token de employee para tests"""
    return get_auth_token("employee_test", TEST_PASSWORDS["employee"])


@pytest.fixture
def test_client():
    """Cliente de pruebas FastAPI"""
    return client
