#!/bin/bash

# Script para construir el frontend Vue.js y copiarlo al backend

echo "🚀 Construyendo panel de administración Vue.js..."

# Navegar al directorio del frontend
cd frontend

# Verificar si existe package.json
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json en el directorio frontend"
    exit 1
fi

# Instalar dependencias si no existen node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Construir el proyecto
echo "🔨 Construyendo proyecto..."
npm run build

# Verificar si la construcción fue exitosa
if [ $? -eq 0 ]; then
    echo "✅ Construcción exitosa"
    
    # Limpiar directorio de destino
    echo "🧹 Limpiando directorio de destino..."
    rm -rf ../www/admin/*
    
    # Copiar archivos construidos
    echo "📋 Copiando archivos a www/admin..."
    cp -r dist/* ../www/admin/
    
    echo "🎉 Panel de administración listo!"
    echo "📍 Accesible en: http://localhost:8081/admin/"
    
else
    echo "❌ Error durante la construcción"
    exit 1
fi