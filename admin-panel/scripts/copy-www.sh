#!/bin/sh
set -e

echo "📂 Limpiando carpeta destino..."
rm -rf ../backend/www/admin
mkdir -p ../backend/www/admin

echo "📦 Copiando archivos..."
cp -r dist/* ../backend/www/admin/

echo "✅ Panel disponible en: http://localhost:8081/admin/"
