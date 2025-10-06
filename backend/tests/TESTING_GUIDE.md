# 📖 Developer Testing Guide

## 🎯 Introduction

This guide provides complete instructions for running all tests in the Face Recognition Backend system. The system includes unit tests, integration tests, and role-protected endpoint tests with warehouse-based authentication.

## 🏗️ Testing Architecture

### Testing File Structure

```
tests/
├── conftest.py                 # Common configuration and fixtures
├── test_auth_unified.py       # Unified authentication tests
├── test_endpoints_unified.py  # Protected endpoint tests
├── test_face_recognition.py   # Face recognition tests
└── test_services.py          # Business service tests
```

### Execution Scripts

```
run_tests.sh              # Main script for all tests
run_integration_tests.sh  # Specific script for integration tests
```

## 🔧 Initial Setup

### 1. Install Dependencies

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov coverage httpx

# Or install from requirements.txt
pip install -r requirements.txt
```

### 2. Configure Test Database

The system uses a unified SQLite database for all tests with warehouse-based architecture:

- **File**: `test_unified.db` (created/deleted automatically)
- **Fixtures**: Configured in `conftest.py`
- **Isolation**: Each test runs in a separate transaction
- **Architecture**: Company → Warehouse → Users (warehouse-based permissions)

### 3. Verify Configuration

```bash
# Verify pytest is available
pytest --version

# Verify test structure
pytest --collect-only tests/
```

## 🚀 Running Tests

### Option 1: Automated Script (Recommended)

```bash
# Run complete suite
./run_tests.sh

# Expected result:
# ✅ Authentication tests: PASSED
# ✅ Endpoint tests: PASSED
# ✅ Integration suite: PASSED
# ✅ Coverage report generated
```

### Option 2: Manual Commands

#### Authentication Tests
```bash
# Run only authentication tests
pytest tests/test_auth_unified.py -v

# With failure details
pytest tests/test_auth_unified.py -v --tb=long

# Only specific tests
pytest tests/test_auth_unified.py::TestAuthentication::test_login_success_admin -v
```

#### Protected Endpoint Tests
```bash
# Run only endpoint tests
pytest tests/test_endpoints_unified.py -v

# By test class
pytest tests/test_endpoints_unified.py::TestWarehouseAccess -v
```

#### Complete Suite
```bash
# All unified tests
pytest tests/test_auth_unified.py tests/test_endpoints_unified.py -v

# With coverage report
pytest tests/test_auth_unified.py tests/test_endpoints_unified.py --cov=. --cov-report=html
```

### Option 3: Integration Tests

```bash
# Requires server running on port 8081
uvicorn main:app --host 0.0.0.0 --port 8081 --reload &

# Run integration tests
./run_integration_tests.sh
```

## 📊 Types of Tests

### 1. Authentication Tests (`test_auth_unified.py`)

**Coverage: 25 tests**

| Category         | Tests | Description                                 |
|------------------|-------|---------------------------------------------|
| Basic login      | 6     | Username/email, invalid credentials         |
| Auth endpoints   | 2     | `/auth/me`, token validation                |
| User registration| 6     | Role permissions, validations               |
| User management  | 4     | CRUD with access control                    |
| Company management| 3    | Role-based operations                       |
| Edge cases       | 4     | Invalid/duplicate tokens                    |

**Execution examples:**
```bash
# Only login tests
pytest tests/test_auth_unified.py::TestAuthentication -v

# Only registration tests
pytest tests/test_auth_unified.py::TestUserRegistration -v

# Specific test
pytest tests/test_auth_unified.py::TestAuthentication::test_login_success_admin -v
```

### 2. Endpoint Tests (`test_endpoints_unified.py`)

**Coverage: 21 tests**

| Category         | Tests | Description                                 |
|------------------|-------|---------------------------------------------|
| Warehouse access | 4     | Company and role-based control              |
| Employee access  | 3     | Listing restrictions                        |
| User CRUD        | 5     | Operations with permissions                 |
| User deletion    | 3     | Controlled deletion                         |
| Company ops      | 2     | Company management                          |
| Security         | 3     | JWT validation                              |
| Permission matrix| 1     | Complete permission matrix                  |

**Execution examples:**
```bash
# Only warehouse tests
pytest tests/test_endpoints_unified.py::TestWarehouseAccess -v

# Only security tests
pytest tests/test_endpoints_unified.py::TestSecurityValidation -v
```

### 3. Integration Tests

**Executed with `run_integration_tests.sh`:**

- Complete admin/manager/employee flows
- End-to-end CRUD operations
- Cross-company restriction validation
- Basic load tests

## 🎭 Fixtures and Test Data

### Available Fixtures (conftest.py)

```python
# Database fixtures
@pytest.fixture
def test_db():          # Session database
def db_session():       # Session per test
def setup_test_data():  # Standard data

# Authentication fixtures
@pytest.fixture
def admin_token():      # Admin token
def manager_token():    # Manager token  
def employee_token():   # Employee token

# Client fixture
@pytest.fixture
def test_client():      # FastAPI client
```

### Standard Test Data

**Users created automatically:**
```python
- admin_test (admin@test.com) - Company 1, Role: admin
- manager_test (manager@test.com) - Company 1, Role: manager
- employee_test (employee@test.com) - Company 1, Role: employee
- manager2_test (manager2@test.com) - Company 2, Role: manager
```

**Companies:**
```python
- Company 1: "Test Company A"
- Company 2: "Test Company B"
```

**Warehouses:**
```python
- Warehouse 1,2: Company 1
- Warehouse 3: Company 2
```

## 📈 Coverage Analysis

### Generate Coverage Report

```bash
# Execute with coverage
coverage run -m pytest tests/test_auth_unified.py tests/test_endpoints_unified.py

# Terminal report
coverage report --show-missing

# HTML report
coverage html
# View at: htmlcov/index.html
```

### Expected Metrics

- **Target coverage**: >85%
- **Critical files**: 100% (auth, dependencies)
- **Controllers**: >90%
- **Services**: >80%

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Error
```bash
# Error: sqlite3.OperationalError: database is locked
# Solution: Clean up test files
rm -f tests/*.db
```

#### 2. Import Failures
```bash
# Error: ModuleNotFoundError
# Solution: Run from backend directory
cd /path/to/backend
pytest tests/
```

#### 3. Hanging Tests
```bash
# Test timeout
# Solution: Run with timeout
pytest tests/ --timeout=30
```

#### 4. Fixture Conflicts
```bash
# Error: fixture not found
# Solution: Check conftest.py
pytest --fixtures tests/
```

### Debug Logs

```bash
# Run with detailed logs
pytest tests/ -v -s --log-cli-level=DEBUG

# Only errors
pytest tests/ -q --tb=short

# Stop on first failure
pytest tests/ -x
```

## 🔄 Development Flow

### Before Committing

```bash
# 1. Run linting
ruff check .

# 2. Run full test suite
./run_tests.sh

# 3. Check coverage
coverage report --fail-under=80
```

### For New Features

```bash
# 1. Write test first (TDD)
# 2. Implement feature
# 3. Run specific tests
pytest tests/test_new_feature.py -v

# 4. Run full suite
./run_tests.sh
```

### CI/CD Pipeline

```bash
# Recommended pipeline:
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run linting
ruff check .

# 3. Run tests with coverage
coverage run -m pytest tests/

# 4. Generate coverage report
coverage report --fail-under=80

# 5. Run integration tests
./run_integration_tests.sh
```

## 📚 Additional References

### Testing Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

### Specific Test Examples

#### Authentication Test
```python
def test_custom_auth(setup_test_data):
    response = client.post("/auth/login", json={
        "username_or_email": "admin_test",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### Protected Endpoint Test
```python
def test_protected_endpoint(admin_token):
    response = client.get("/protected-endpoint", 
        headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
```

#### Test with Custom Data
```python
def test_with_custom_data(db_session):
    # Create specific data for this test
    user = User(username="test_user", ...)
    db_session.add(user)
    db_session.commit()
    
    # Run test
    # ...
```

## 🎯 Conclusion

This testing system provides:

- ✅ **Complete coverage** of critical features
- ✅ **Isolation** between tests for consistency
- ✅ **Automated scripts** for easy execution
- ✅ **Reusable fixtures** for efficiency
- ✅ **Clear documentation** for new developers

**Quick command to run everything:**
```bash
./run_tests.sh && echo "🎉 All tests successful!"
```