@echo off
REM Script para construir el frontend Vue.js y copiarlo al backend (Windows)

echo 🚀 Construyendo panel de administración Vue.js...

REM Navegar al directorio del frontend
cd frontend

REM Verificar si existe package.json
if not exist "package.json" (
    echo ❌ Error: No se encontró package.json en el directorio frontend
    exit /b 1
)

REM Instalar dependencias si no existen node_modules
if not exist "node_modules" (
    echo 📦 Instalando dependencias...
    npm install
)

REM Construir el proyecto
echo 🔨 Construyendo proyecto...
npm run build

REM Verificar si la construcción fue exitosa
if %errorlevel% equ 0 (
    echo ✅ Construcción exitosa
    
    REM Limpiar directorio de destino
    echo 🧹 Limpiando directorio de destino...
    if exist "..\www\admin" rmdir /s /q "..\www\admin"
    mkdir "..\www\admin"
    
    REM Copiar archivos construidos
    echo 📋 Copiando archivos a www/admin...
    xcopy /e /y "dist\*" "..\www\admin\"
    
    echo 🎉 Panel de administración listo!
    echo 📍 Accesible en: http://localhost:8081/admin/
    
) else (
    echo ❌ Error durante la construcción
    exit /b 1
)