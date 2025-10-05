#!/bin/bash

# Script para ejecutar todas las pruebas unitarias
# Face Recognition Backend Test Suite

set -e  # Salir si algún comando falla

echo "🧪 INICIANDO SUITE DE PRUEBAS - Face Recognition Backend"
echo "========================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    log_error "Debe ejecutar este script desde el directorio backend"
    exit 1
fi

# Verificar que pytest está instalado
if ! command -v pytest &> /dev/null; then
    log_error "pytest no está instalado. Ejecute: pip install pytest pytest-asyncio"
    exit 1
fi

# Limpiar archivos de prueba anteriores
log_info "Limpiando archivos de prueba anteriores..."
rm -f tests/test_*.db tests/test_unified.db

# Ejecutar linting básico si ruff está disponible
if command -v ruff &> /dev/null; then
    log_info "Ejecutando análisis de código con ruff..."
    ruff check tests/ --select E,W,F || log_warning "Se encontraron algunos warnings de estilo"
fi

echo ""
echo "🧪 EJECUTANDO PRUEBAS UNITARIAS"
echo "================================"

# 1. Pruebas de Autenticación
log_info "Ejecutando pruebas de autenticación..."
pytest tests/test_auth_unified.py -v --tb=short
if [ $? -eq 0 ]; then
    log_success "✅ Pruebas de autenticación completadas"
else
    log_error "❌ Fallos en pruebas de autenticación"
    exit 1
fi

echo ""

# 2. Pruebas de Endpoints Protegidos
log_info "Ejecutando pruebas de endpoints protegidos..."
pytest tests/test_endpoints_unified.py -v --tb=short
if [ $? -eq 0 ]; then
    log_success "✅ Pruebas de endpoints completadas"
else
    log_error "❌ Fallos en pruebas de endpoints"
    exit 1
fi

echo ""

# 3. Pruebas de Reconocimiento Facial (si existen)
if [ -f "tests/test_face_recognition.py" ]; then
    log_info "Ejecutando pruebas de reconocimiento facial..."
    pytest tests/test_face_recognition.py -v --tb=short
    if [ $? -eq 0 ]; then
        log_success "✅ Pruebas de reconocimiento facial completadas"
    else
        log_warning "⚠️  Algunas pruebas de reconocimiento facial fallaron"
    fi
    echo ""
fi

# 4. Ejecutar todas las pruebas juntas para verificar integración
log_info "Ejecutando suite completa de integración..."
pytest tests/test_auth_unified.py tests/test_endpoints_unified.py -v --tb=short --durations=10
if [ $? -eq 0 ]; then
    log_success "✅ Suite completa de integración exitosa"
else
    log_error "❌ Fallos en la integración completa"
    exit 1
fi

echo ""
echo "📊 RESUMEN DE COBERTURA"
echo "======================="

# Ejecutar con cobertura si coverage está disponible
if command -v coverage &> /dev/null; then
    log_info "Generando reporte de cobertura..."
    coverage run -m pytest tests/test_auth_unified.py tests/test_endpoints_unified.py --quiet
    coverage report --show-missing
    coverage html
    log_success "Reporte de cobertura generado en htmlcov/"
else
    log_warning "coverage no está instalado. Para cobertura: pip install coverage"
fi

echo ""
echo "🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE"
echo "=============================================="
log_success "Suite de pruebas unitarias: PASSED"
log_success "Suite de pruebas de integración: PASSED"
log_info "Limpiar archivos temporales..."
rm -f tests/test_unified.db

echo ""
log_info "Para ejecutar pruebas específicas:"
echo "  - Autenticación: pytest tests/test_auth_unified.py -v"
echo "  - Endpoints: pytest tests/test_endpoints_unified.py -v"
echo "  - Integración: pytest tests/test_auth_unified.py tests/test_endpoints_unified.py -v"