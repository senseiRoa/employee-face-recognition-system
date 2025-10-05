@echo off
echo.
echo ========================================
echo  🚀 PANEL DE ADMINISTRACION - VUE.JS
echo ========================================
echo.
echo Selecciona el modo de desarrollo:
echo.
echo 1. Desarrollo completo (Hot Reload + Proxy)
echo 2. Integracion completa (Build + FastAPI)
echo 3. Solo construir para produccion
echo 4. Ayuda
echo.
set /p choice="Elige una opcion (1-4): "

if "%choice%"=="1" goto dev_mode
if "%choice%"=="2" goto integrated_mode  
if "%choice%"=="3" goto build_mode
if "%choice%"=="4" goto help
goto invalid

:dev_mode
echo.
echo 🔥 Iniciando modo desarrollo...
echo 📍 admin-panel: http://localhost:3000 (o puerto automatico)
echo 📍 Asegurate de que el backend este corriendo en puerto 8081
echo.
cd admin-panel
npm run dev
goto end

:integrated_mode
echo.
echo 🏭 Construyendo e integrando con FastAPI...
cd admin-panel
npm run build:prod:win
echo.
echo ✅ Panel disponible en: http://localhost:8081/admin/
echo 💡 Asegurate de que FastAPI este ejecutandose
goto end

:build_mode
echo.
echo 📦 Construyendo para produccion...
cd admin-panel
npm run build:prod:win
echo.
echo ✅ Build completado en /dist
echo 💡 Para integrar ejecuta: npm run copy-to-www
goto end

:help
echo.
echo 📚 AYUDA - MODOS DE DESARROLLO
echo.
echo MODO 1 - DESARROLLO:
echo   - Hot reload instantaneo
echo   - Vue DevTools disponible
echo   - Proxy automatico al backend
echo   - Mejor para desarrollo activo
echo.
echo MODO 2 - INTEGRADO:
echo   - Comportamiento de produccion
echo   - Un solo puerto (8081)
echo   - Perfecto para testing final
echo.
echo MODO 3 - SOLO BUILD:
echo   - Solo construye archivos
echo   - No copia automaticamente
echo   - Para CI/CD o deployment manual
echo.
echo REQUISITOS:
echo   - Node.js 16+
echo   - Backend FastAPI en puerto 8081
echo.
pause
goto end

:invalid
echo.
echo ❌ Opcion invalida. Ejecuta el script nuevamente.
pause
goto end

:end
echo.
pause