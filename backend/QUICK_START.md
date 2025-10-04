# 🚀 Quick Start - Checklist de Implementación

## ⚡ Pasos Rápidos para Ejecutar

### ✅ Paso 1: Verificar ruta inicial
```bash
cd /workspaces/face_recognition_test/backend


```

### ✅ Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Verificar instalación:**
```bash
python -c "import bcrypt; import jose; import passlib; print('✅ Todas las dependencias instaladas')"
```

### ✅ Paso 3: Configurar Variables de Entorno
```bash
# Editar .env
nano .env
```

**Agregar/verificar:**
```env
# Database
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_DATABASE=employee_tracker
DB_PORT=3306

# JWT (IMPORTANTE: Cambiar en producción)
JWT_SECRET_KEY=change-this-to-a-random-secure-key-minimum-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### ✅ Paso 4: Backup de Base de Datos (Recomendado)
```bash
# Solo si tienes datos importantes con cliente mysql
mysqldump -u root -p employee_tracker > backup_before_migration.sql
```

### ✅ Paso 5: Generar Migración de Alembic
```bash
# Ver estado actual
alembic current

# Generar migración automática
alembic revision --autogenerate -m "xxxxxxxx"
```

**⚠️ IMPORTANTE:** Revisa el archivo generado en `alembic/versions/`



### ✅ Paso 6: Aplicar Migración
```bash
# Aplicar
alembic upgrade head

# Verificar
alembic current
```

**Si algo sale mal:**
```bash
# Revertir
alembic downgrade -1

# Ver historial
alembic history
```

### ✅ Paso 7: Inicializar Roles (para la primera vez que se ejecuta con base de datos limpia)
```bash
# Solo roles
python init_database.py

# Con datos de prueba (recomendado para desarrollo)
python init_database.py --test-data
```

**Salida esperada:**
```
🔧 Inicializando roles predefinidos...
✅ Roles inicializados
```

### ✅ Paso 8: Ejecutar el Servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000 o F5 en vscode
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### ✅ Paso 9: Verificar Endpoints
```bash
# Health check (sin auth)
curl http://localhost:8000/health

# Debería retornar: {"status":"ok"}
```

Abrir en navegador: http://localhost:8000/docs

### ✅ Paso 10: Probar API

**1. Registrar empresa:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "username": "testuser",
    "password": "test123"
  }'
```

**2. Guardar el token:**
```bash
export TOKEN="<token_recibido>"
```

**3. Verificar autenticación:**
```bash
curl http://localhost:8000/companies/me \
  -H "Authorization: Bearer $TOKEN"
```

**4. Listar roles:**
```bash
curl http://localhost:8000/roles \
  -H "Authorization: Bearer $TOKEN"
```

**Deberías ver 4 roles:** AdminTablet, AdminWeb, Supervisor, Empleado

---

## 🐛 Troubleshooting Rápido

### Error: Module not found
```bash
pip install -r requirements.txt --upgrade
```

### Error: Database connection
```bash
# Verificar MySQL está corriendo
sudo systemctl status mysql

# Verificar credenciales
mysql -h host.docker.internal -P 3307 -u root -p'timeTrackerDB' --password='m634kkkd/*ss'

```
¡Si lograste la comunicacion , Excelente! 🙌 Aquí tienes una **tabla resumida de comandos útiles de MySQL** que puedes ejecutar desde el cliente (`mysql -u ...`).

---

### 📊 Comandos básicos de MySQL

| Comando                                               | Descripción                                                |
| ----------------------------------------------------- | ---------------------------------------------------------- |
| `mysql -h host -P puerto -u usuario -p`               | Conectarse al servidor MySQL (pedirá contraseña).          |
| `SHOW DATABASES;`                                     | Listar todas las bases de datos disponibles.               |
| `USE nombre_db;`                                      | Seleccionar una base de datos para trabajar.               |
| `SHOW TABLES;`                                        | Listar todas las tablas de la base de datos seleccionada.  |
| `DESCRIBE nombre_tabla;` o `DESC nombre_tabla;`       | Mostrar estructura de una tabla (columnas, tipos, claves). |
| `CREATE DATABASE nombre_db;`                          | Crear una nueva base de datos.                             |
| `DROP DATABASE nombre_db;`                            | Eliminar una base de datos (⚠️ irreversible).              |
| `CREATE TABLE nombre_tabla (...);`                    | Crear una tabla nueva.                                     |
| `DROP TABLE nombre_tabla;`                            | Eliminar una tabla.                                        |
| `INSERT INTO nombre_tabla VALUES (...);`              | Insertar un registro en una tabla.                         |
| `SELECT * FROM nombre_tabla;`                         | Consultar todos los registros de una tabla.                |
| `SELECT columna1, columna2 FROM nombre_tabla;`        | Consultar columnas específicas de una tabla.               |
| `UPDATE nombre_tabla SET columna=valor WHERE id=...;` | Actualizar registros existentes.                           |
| `DELETE FROM nombre_tabla WHERE condición;`           | Eliminar registros de una tabla.                           |
| `SHOW PROCESSLIST;`                                   | Ver conexiones y procesos activos en MySQL.                |
| `EXIT;` o `QUIT;`                                     | Salir del cliente MySQL.                                   |

---

👉 ¿Quieres que te arme otra tabla pero solo con **comandos administrativos (usuarios, privilegios, backups)** o prefieres quedarte con esta general de uso diario?


### Error: Alembic no puede generar migración
```bash
# Limpiar cache
rm -rf alembic/versions/__pycache__

# Reintentar
alembic revision --autogenerate -m "migration"
```

### Error: Port already in use
```bash
# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9

# O usar otro puerto
uvicorn main:app --reload --port 8001
```

### Error: Face recognition
```bash
# Instalar dependencias de sistema (Debian/Ubuntu)
sudo apt-get install cmake libopenblas-dev liblapack-dev

# Reinstalar face_recognition
pip uninstall face_recognition dlib
pip install dlib
pip install face_recognition
```

---

## 📋 Checklist de Verificación

Marca cada item cuando esté completo:

- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Backup de BD creado (si aplicable)
- [ ] Migración generada (`alembic revision --autogenerate`)
- [ ] Migración revisada y editada (si necesario)
- [ ] Migración aplicada (`alembic upgrade head`)
- [ ] Roles inicializados (`python init_database.py`)
- [ ] Servidor ejecutándose (`uvicorn main:app --reload`)
- [ ] Health check funciona (`curl /health`)
- [ ] Swagger UI accesible (`http://localhost:8000/docs`)
- [ ] Registro de empresa funciona (`POST /auth/register`)
- [ ] Login funciona (`POST /auth/login`)
- [ ] Endpoints protegidos requieren auth
- [ ] Roles listados correctamente (`GET /roles`)

---

## 🎯 Endpoints Clave para Probar

En orden de prioridad:

1. ✅ `GET /health` - Sin auth
2. ✅ `POST /auth/register` - Crear empresa
3. ✅ `POST /auth/login` - Obtener token
4. ✅ `GET /companies/me` - Verificar auth
5. ✅ `GET /roles` - Ver roles
6. ✅ `POST /warehouses` - Crear warehouse
7. ✅ `POST /tablets` - Registrar tablet
8. ✅ `POST /users` - Crear usuario
9. ✅ `POST /employees/register_face` - Registrar empleado
10. ✅ `POST /employees/check_in_out` - Probar facial
11. ✅ `GET /logs/access` - Ver logs
12. ✅ `GET /reports/checkins` - Ver reportes

---

## 🔗 Recursos Útiles

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Documentation**: `API_ENDPOINTS.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`
- **Migration Example**: `MIGRATION_EXAMPLE.py`

---

## 💡 Consejos

1. **Usa Swagger UI** para probar endpoints interactivamente
2. **Guarda el token** en una variable de entorno para facilitar pruebas
3. **Revisa los logs** si algo no funciona: `tail -f logs/app.log`
4. **Usa datos de prueba** con `--test-data` en desarrollo
5. **Lee IMPLEMENTATION_GUIDE.md** para detalles completos

---

## 🎉 Todo Listo!

Si completaste todos los pasos del checklist:

✅ **El backend está completamente funcional**

Puedes comenzar a:
- Integrar con el frontend de tablets
- Desarrollar el panel web de administración
- Agregar más funcionalidades
- Deploy en producción

---

## 📞 Ayuda Adicional

Si tienes problemas:

1. Lee el error completo
2. Busca en `IMPLEMENTATION_GUIDE.md`
3. Revisa `API_ENDPOINTS.md`
4. Verifica los logs de la aplicación
5. Comprueba la configuración de `.env`

**Errores comunes ya resueltos en docs** ✅

---

**¡Éxito!** 🚀
