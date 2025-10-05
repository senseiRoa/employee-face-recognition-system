@echo off
echo 📂 Limpiando carpeta destino...
if exist ..\backend\www\admin rmdir /s /q ..\backend\www\admin
mkdir ..\backend\www\admin

echo 📦 Copiando archivos...
xcopy dist ..\backend\www\admin /E /I /Y >nul

echo ✅ Panel disponible en: http://localhost:8081/admin/
pause
