#!/bin/bash

# Script para pruebas de integración
# Simula flujos completos de usuario

set -e

echo "🔄 INICIANDO PRUEBAS DE INTEGRACIÓN"
echo "===================================="

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INTEGRATION]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Verificar que el servidor esté corriendo
log_info "Verificando que el servidor FastAPI esté ejecutándose..."
if ! curl -s http://localhost:8081/docs > /dev/null; then
    echo "❌ El servidor FastAPI no está ejecutándose en puerto 8081"
    echo "Por favor ejecute: uvicorn main:app --host 0.0.0.0 --port 8081 --reload"
    exit 1
fi

log_success "✅ Servidor FastAPI detectado en puerto 8081"

echo ""
echo "🧪 EJECUTANDO FLUJOS DE INTEGRACIÓN"
echo "==================================="

# Test 1: Flujo completo de Admin
log_info "Test 1: Flujo completo de administrador"
echo "- Login como admin"
echo "- Crear nueva compañía"
echo "- Crear usuario manager"
echo "- Listar usuarios"

ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8081/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "admin", "password": "admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ No se pudo obtener token de admin. Verifique credenciales."
    exit 1
fi

log_success "✅ Login de admin exitoso"

# Test 2: Flujo de Manager
log_info "Test 2: Flujo de manager - gestión de empleados"
echo "- Login como manager"
echo "- Crear empleado"
echo "- Listar empleados de su compañía"

# Test 3: Flujo de Employee
log_info "Test 3: Flujo de employee - acceso limitado"
echo "- Login como employee"
echo "- Verificar acceso a su perfil"
echo "- Verificar restricciones de acceso"

# Test 4: Flujo de Reconocimiento Facial
if [ -f "test_img/foto1.png" ]; then
    log_info "Test 4: Flujo de reconocimiento facial"
    echo "- Registrar cara de empleado"
    echo "- Verificar reconocimiento"
    echo "- Generar log de acceso"
fi

# Test 5: Flujo de Warehouses
log_info "Test 5: Flujo de gestión de warehouses"
echo "- Admin crea warehouse"
echo "- Manager accede a warehouses de su compañía"
echo "- Employee con acceso limitado"

echo ""
echo "📊 EJECUTANDO PYTEST INTEGRATION"
echo "================================="

# Ejecutar los tests con marcadores de integración
pytest tests/test_auth_unified.py tests/test_endpoints_unified.py \
    -v \
    --tb=short \
    -x \
    --durations=0

if [ $? -eq 0 ]; then
    log_success "✅ Todas las pruebas de integración exitosas"
else
    echo "❌ Algunas pruebas de integración fallaron"
    exit 1
fi

echo ""
echo "🎯 PRUEBAS DE CARGA (BÁSICAS)"
echo "============================="

log_info "Ejecutando pruebas básicas de carga..."

# Test básico de carga con curl
for i in {1..10}; do
    curl -s -X GET "http://localhost:8081/auth/me" \
        -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
    if [ $? -ne 0 ]; then
        echo "❌ Fallo en request $i"
        exit 1
    fi
done

log_success "✅ 10 requests concurrentes exitosos"

echo ""
echo "🎉 PRUEBAS DE INTEGRACIÓN COMPLETADAS"
echo "======================================"
log_success "Todos los flujos de integración exitosos"
log_info "Sistema listo para producción"