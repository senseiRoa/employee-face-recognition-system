# 📖 Guía de Testing para Desarrolladores

## 🎯 Introducción

Esta guía proporciona instrucciones completas para ejecutar todas las pruebas del sistema de Face Recognition Backend. El sistema incluye pruebas unitarias, de integración y de endpoints protegidos con autenticación por roles.

## 🏗️ Arquitectura de Testing

### Estructura de Archivos de Testing

```
tests/
├── conftest.py                 # Configuración común y fixtures
├── test_auth_unified.py       # Pruebas de autenticación unificadas
├── test_endpoints_unified.py  # Pruebas de endpoints protegidos
├── test_face_recognition.py   # Pruebas de reconocimiento facial
└── test_services.py          # Pruebas de servicios de negocio
```

### Scripts de Ejecución

```
run_tests.sh              # Script principal para todas las pruebas
run_integration_tests.sh  # Script específico para pruebas de integración
```

## 🔧 Configuración Inicial

### 1. Instalar Dependencias

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio pytest-cov coverage httpx

# O instalar desde requirements.txt
pip install -r requirements.txt
```

### 2. Configurar Base de Datos de Prueba

El sistema utiliza una base de datos SQLite unificada para todas las pruebas:

- **Archivo**: `test_unified.db` (se crea/elimina automáticamente)
- **Fixtures**: Configuradas en `conftest.py`
- **Aislamiento**: Cada test ejecuta en una transacción separada

### 3. Verificar Configuración

```bash
# Verificar que pytest está disponible
pytest --version

# Verificar estructura de tests
pytest --collect-only tests/
```

## 🚀 Ejecutar Pruebas

### Opción 1: Script Automatizado (Recomendado)

```bash
# Ejecutar suite completa
./run_tests.sh

# Resultado esperado:
# ✅ Pruebas de autenticación: PASSED
# ✅ Pruebas de endpoints: PASSED
# ✅ Suite de integración: PASSED
# ✅ Reporte de cobertura generado
```

### Opción 2: Comandos Manuales

#### Pruebas de Autenticación
```bash
# Ejecutar solo pruebas de autenticación
pytest tests/test_auth_unified.py -v

# Con detalles de fallos
pytest tests/test_auth_unified.py -v --tb=long

# Solo tests específicos
pytest tests/test_auth_unified.py::TestAuthentication::test_login_success_admin -v
```

#### Pruebas de Endpoints Protegidos
```bash
# Ejecutar solo pruebas de endpoints
pytest tests/test_endpoints_unified.py -v

# Por clase de test
pytest tests/test_endpoints_unified.py::TestWarehouseAccess -v
```

#### Suite Completa
```bash
# Todas las pruebas unificadas
pytest tests/test_auth_unified.py tests/test_endpoints_unified.py -v

# Con reporte de cobertura
pytest tests/test_auth_unified.py tests/test_endpoints_unified.py --cov=. --cov-report=html
```

### Opción 3: Pruebas de Integración

```bash
# Requiere servidor corriendo en puerto 8081
uvicorn main:app --host 0.0.0.0 --port 8081 --reload &

# Ejecutar pruebas de integración
./run_integration_tests.sh
```

## 📊 Tipos de Pruebas

### 1. Pruebas de Autenticación (`test_auth_unified.py`)

**Cobertura: 25 tests**

| Categoría | Tests | Descripción |
|-----------|-------|-------------|
| Login básico | 6 tests | Username/email, credenciales inválidas |
| Endpoints auth | 2 tests | `/auth/me`, validación de tokens |
| Registro usuarios | 6 tests | Permisos por rol, validaciones |
| Gestión usuarios | 4 tests | CRUD con control de acceso |
| Gestión compañías | 3 tests | Operaciones por rol |
| Edge cases | 4 tests | Tokens inválidos, duplicados |

**Ejemplos de ejecución:**
```bash
# Solo tests de login
pytest tests/test_auth_unified.py::TestAuthentication -v

# Solo tests de registro
pytest tests/test_auth_unified.py::TestUserRegistration -v

# Test específico
pytest tests/test_auth_unified.py::TestAuthentication::test_login_success_admin -v
```

### 2. Pruebas de Endpoints (`test_endpoints_unified.py`)

**Cobertura: 21 tests**

| Categoría | Tests | Descripción |
|-----------|-------|-------------|
| Warehouse access | 4 tests | Control por compañía y rol |
| Employee access | 3 tests | Restricciones de listado |
| User CRUD | 5 tests | Operaciones con permisos |
| User deletion | 3 tests | Eliminación controlada |
| Company ops | 2 tests | Gestión de compañías |
| Security | 3 tests | Validación JWT |
| Permission matrix | 1 test | Matriz completa de permisos |

**Ejemplos de ejecución:**
```bash
# Solo tests de warehouses
pytest tests/test_endpoints_unified.py::TestWarehouseAccess -v

# Solo tests de seguridad
pytest tests/test_endpoints_unified.py::TestSecurityValidation -v
```

### 3. Pruebas de Integración

**Ejecutadas con `run_integration_tests.sh`:**

- Flujos completos de admin/manager/employee
- Operaciones CRUD end-to-end
- Validación de restricciones cross-company
- Pruebas básicas de carga

## 🎭 Fixtures y Datos de Prueba

### Fixtures Disponibles (conftest.py)

```python
# Fixtures de base de datos
@pytest.fixture
def test_db():          # Base de datos de sesión
def db_session():       # Sesión por test
def setup_test_data():  # Datos estándar

# Fixtures de autenticación
@pytest.fixture
def admin_token():      # Token de admin
def manager_token():    # Token de manager  
def employee_token():   # Token de employee

# Fixture de cliente
@pytest.fixture
def test_client():      # Cliente FastAPI
```

### Datos de Prueba Estándar

**Usuarios creados automáticamente:**
```python
- admin_test (admin@test.com) - Company 1, Role: admin
- manager_test (manager@test.com) - Company 1, Role: manager
- employee_test (employee@test.com) - Company 1, Role: employee
- manager2_test (manager2@test.com) - Company 2, Role: manager
```

**Compañías:**
```python
- Company 1: "Test Company A"
- Company 2: "Test Company B"
```

**Warehouses:**
```python
- Warehouse 1,2: Company 1
- Warehouse 3: Company 2
```

## 📈 Análisis de Cobertura

### Generar Reporte de Cobertura

```bash
# Ejecutar con cobertura
coverage run -m pytest tests/test_auth_unified.py tests/test_endpoints_unified.py

# Reporte en terminal
coverage report --show-missing

# Reporte HTML
coverage html
# Ver en: htmlcov/index.html
```

### Métricas Esperadas

- **Cobertura objetivo**: >85%
- **Archivos críticos**: 100% (auth, dependencies)
- **Controllers**: >90%
- **Services**: >80%

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Error de Base de Datos
```bash
# Error: sqlite3.OperationalError: database is locked
# Solución: Limpiar archivos de prueba
rm -f tests/*.db
```

#### 2. Imports Fallando
```bash
# Error: ModuleNotFoundError
# Solución: Ejecutar desde directorio backend
cd /path/to/backend
pytest tests/
```

#### 3. Tests Colgando
```bash
# Timeout en tests
# Solución: Ejecutar con timeout
pytest tests/ --timeout=30
```

#### 4. Conflictos de Fixtures
```bash
# Error: fixture not found
# Solución: Verificar conftest.py
pytest --fixtures tests/
```

### Logs de Debug

```bash
# Ejecutar con logs detallados
pytest tests/ -v -s --log-cli-level=DEBUG

# Solo errores
pytest tests/ -q --tb=short

# Parar en primer fallo
pytest tests/ -x
```

## 🔄 Flujo de Desarrollo

### Antes de Hacer Commit

```bash
# 1. Ejecutar linting
ruff check .

# 2. Ejecutar tests completos
./run_tests.sh

# 3. Verificar cobertura
coverage report --fail-under=80
```

### Para Nuevas Features

```bash
# 1. Escribir test primero (TDD)
# 2. Implementar feature
# 3. Ejecutar tests específicos
pytest tests/test_new_feature.py -v

# 4. Ejecutar suite completa
./run_tests.sh
```

### CI/CD Pipeline

```bash
# Pipeline recomendado:
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

## 📚 Referencias Adicionales

### Documentación de Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

### Ejemplos de Tests Específicos

#### Test de Autenticación
```python
def test_custom_auth(setup_test_data):
    response = client.post("/auth/login", json={
        "username_or_email": "admin_test",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### Test de Endpoint Protegido
```python
def test_protected_endpoint(admin_token):
    response = client.get("/protected-endpoint", 
        headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
```

#### Test con Datos Personalizados
```python
def test_with_custom_data(db_session):
    # Crear datos específicos para este test
    user = User(username="test_user", ...)
    db_session.add(user)
    db_session.commit()
    
    # Ejecutar test
    # ...
```

## 🎯 Conclusión

Este sistema de testing proporciona:

- ✅ **Cobertura completa** de funcionalidades críticas
- ✅ **Aislamiento** entre tests para consistencia
- ✅ **Scripts automatizados** para facilitar ejecución
- ✅ **Fixtures reutilizables** para eficiencia
- ✅ **Documentación clara** para nuevos desarrolladores

**Comando rápido para ejecutar todo:**
```bash
./run_tests.sh && echo "🎉 Todos los tests exitosos!"
```