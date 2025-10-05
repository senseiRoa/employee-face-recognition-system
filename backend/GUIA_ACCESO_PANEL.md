# 🔐 Guía de Acceso al Panel de Administración

## 📍 URL de Acceso
**Panel de Administración**: `http://localhost:8081/admin/`

## 🔑 Credenciales de Acceso

### Credenciales por Defecto
- **Usuario**: `admin`  
- **Contraseña**: `Admin123!`

### Formato de Login
El sistema acepta tanto **usuario** como **email** en el campo "Usuario o Email".

## 🚀 Primeros Pasos

1. **Acceder al Panel**
   - Abrir navegador en `http://localhost:8081/admin/`
   - Será redirigido automáticamente a `/admin/login`

2. **Iniciar Sesión**
   - Ingresar `admin` en el campo "Usuario o Email"
   - Ingresar `Admin123!` en el campo "Contraseña"
   - Hacer clic en "Iniciar Sesión"

3. **Navegación**
   - Será redirigido al Dashboard principal
   - Usar el sidebar izquierdo para navegar entre secciones

## 📋 Secciones Disponibles

### 📊 Dashboard
- **URL**: `/admin/dashboard`
- **Descripción**: Panel principal con métricas y estadísticas
- **Características**:
  - Métricas de empresas, warehouses y empleados
  - Gráficos de actividad semanal
  - Actividad reciente del sistema

### 🏢 Gestión de Empresas  
- **URL**: `/admin/companies`
- **Funciones**: Crear, editar, eliminar y listar empresas
- **Campos**: Nombre, email, teléfono, dirección, estado

### 🏭 Gestión de Warehouses
- **URL**: `/admin/warehouses`  
- **Funciones**: Administrar warehouses vinculados a empresas
- **Campos**: Nombre, ubicación, empresa asociada, estado

### 👥 Gestión de Empleados
- **URL**: `/admin/employees`
- **Funciones**: Administrar empleados con reconocimiento facial
- **Características**:
  - Carga de fotos para reconocimiento facial
  - Asignación a warehouses
  - Control de estado activo/inactivo

### 👤 Gestión de Usuarios
- **URL**: `/admin/users`
- **Funciones**: Administrar usuarios internos del sistema
- **Campos**: Usuario, email, contraseña, rol asignado

### 🔑 Gestión de Roles
- **URL**: `/admin/roles`
- **Funciones**: Definir roles y permisos del sistema
- **Características**:
  - Permisos granulares
  - Asignación múltiple de permisos

### 📋 Auditoría y Logs
- **URL**: `/admin/logs`
- **Funciones**: Visualizar actividad del sistema
- **Características**:
  - Filtros por fecha, empleado, tipo de acción
  - Paginación de resultados
  - Exportación de logs
  - Detalles expandibles de eventos

### 📈 Reportes
- **URL**: `/admin/reports`
- **Funciones**: Generar y descargar reportes
- **Características**:
  - Múltiples formatos (PDF, CSV, Excel)
  - Filtros personalizables por fechas
  - Estadísticas visuales
  - Historial de reportes generados

## 🔧 Solución de Problemas Comunes

### ❌ Error: "Error de autenticación"
- **Causa**: Credenciales incorrectas
- **Solución**: Verificar que las credenciales sean `admin` / `Admin123!`

### ❌ Error: "Error de conexión"  
- **Causa**: Backend no está funcionando
- **Solución**: Verificar que FastAPI esté corriendo en puerto 8081
- **Comando**: `uvicorn main:app --host 0.0.0.0 --port 8081 --reload`

### ❌ Panel no carga (404)
- **Causa**: Frontend no está compilado o copiado correctamente
- **Solución**: Reconstruir frontend
- **Comandos**: 
  ```bash
  cd frontend
  npm run build
  cp -r dist/* ../www/admin/
  ```

### ❌ API calls fallan
- **Causa**: Endpoints no coinciden entre frontend y backend
- **Verificación**: Los endpoints del backend son:
  - `/auth/login` (login)
  - `/companies/` (empresas)
  - `/warehouses/` (warehouses)
  - `/employees/` (empleados)
  - `/users/` (usuarios)
  - `/roles/` (roles)
  - `/logs/` (logs)
  - `/reports/` (reportes)

## 🔒 Seguridad

### Token JWT
- **Duración**: Configurada en el backend
- **Storage**: localStorage del navegador  
- **Renovación**: Automática en cada petición válida
- **Expiración**: Redirección automática a login

### Permisos
- **Admin**: Acceso completo a todas las funciones
- **Manager**: Acceso limitado según configuración de roles
- **Employee**: Acceso restringido a funciones básicas

## 📱 Compatibilidad

### Navegadores Soportados
- ✅ Chrome 90+
- ✅ Firefox 88+  
- ✅ Safari 14+
- ✅ Edge 90+

### Dispositivos
- ✅ **Desktop**: Experiencia completa
- ✅ **Tablet**: Interfaz adaptativa con sidebar colapsible
- ✅ **Mobile**: Diseño responsive optimizado

## 🆘 Soporte

### Logs del Sistema
- **Backend**: Consola donde se ejecuta uvicorn
- **Frontend**: DevTools del navegador (F12)

### Endpoints de Verificación
- **Health Check**: `http://localhost:8081/health`
- **API Docs**: `http://localhost:8081/docs`
- **Panel**: `http://localhost:8081/admin/`

### Comandos Útiles
```bash
# Verificar servidor
curl http://localhost:8081/health

# Probar autenticación
curl -X POST http://localhost:8081/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "admin", "password": "Admin123!"}'

# Reconstruir frontend
cd frontend && npm run build && cp -r dist/* ../www/admin/
```

---

## ✅ Panel Funcionando Correctamente

Si puedes ver esta guía, significa que el panel de administración está funcionando correctamente en:

**🌐 http://localhost:8081/admin/**

¡Disfruta utilizando el sistema! 🚀