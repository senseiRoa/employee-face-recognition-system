# Panel de Administración - Vue.js

Panel de administración web desarrollado con Vue.js 3 para el sistema de reconocimiento facial de empleados.

## 🚀 Características

- **Gestión completa**: Empresas, warehouses, empleados, usuarios y roles
- **Dashboard interactivo**: Métricas en tiempo real y gráficos
- **Auditoría**: Logs completos de actividad y accesos
- **Reportes**: Generación y exportación de reportes
- **Responsive**: Optimizado para desktop y móvil
- **Autenticación**: JWT integrado con el backend FastAPI

## 📋 Requisitos

- Node.js 16+ 
- npm o yarn
- Backend FastAPI ejecutándose en puerto 8081

## 🛠️ Instalación y Desarrollo

### 1. Instalar dependencias
```bash
cd frontend
npm install
```

### 2. Desarrollo local
```bash
npm run dev
```
El servidor de desarrollo estará disponible en `http://localhost:3000`

### 3. Construcción para producción
```bash
npm run build
```

### 4. Construcción y despliegue automático
```bash
# En el directorio raíz del backend
./build_frontend.sh   # Linux/Mac
build_frontend.bat    # Windows
```

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── assets/           # CSS y recursos estáticos
│   ├── components/       # Componentes reutilizables
│   │   └── Layout.vue    # Layout principal con sidebar
│   ├── composables/      # Hooks para API calls
│   │   ├── api.js        # Configuración de axios
│   │   ├── useCompanies.js
│   │   ├── useEmployees.js
│   │   └── useWarehouses.js
│   ├── router/           # Configuración de Vue Router
│   ├── store/            # Estado global con Pinia
│   │   ├── auth.js       # Autenticación
│   │   └── app.js        # Estado de la aplicación
│   ├── views/            # Vistas principales
│   │   ├── Dashboard.vue
│   │   ├── Companies.vue
│   │   ├── Employees.vue
│   │   ├── Warehouses.vue
│   │   ├── Users.vue
│   │   ├── Roles.vue
│   │   ├── Logs.vue
│   │   └── Reports.vue
│   ├── App.vue
│   └── main.js
├── package.json
├── vite.config.js
└── index.html
```

## 🔧 Configuración

### Variables de Entorno (opcional)
Crear `.env.local` en el directorio `frontend/`:
```
VITE_API_URL=http://localhost:8081
```

### Proxy de desarrollo
El archivo `vite.config.js` ya está configurado para hacer proxy de las peticiones API al backend en desarrollo.

## 🎯 Funcionalidades

### 🏢 Gestión de Empresas
- CRUD completo de empresas
- Campos: nombre, email, teléfono, dirección
- Estado activo/inactivo

### 🏭 Gestión de Warehouses  
- CRUD de warehouses vinculados a empresas
- Asignación de empleados
- Control de estado

### 👥 Gestión de Empleados
- Registro de empleados con foto
- Codificación facial automática (base64)
- Asignación a warehouses
- Control de estado activo/inactivo

### 👤 Gestión de Usuarios
- Usuarios internos del sistema
- Asignación de roles y permisos
- Control de acceso

### 🔑 Gestión de Roles
- Definición de roles personalizados
- Permisos granulares
- Asignación a usuarios

### 📊 Dashboard
- Métricas en tiempo real
- Gráficos de actividad
- Estadísticas de check-ins
- Actividad reciente

### 📋 Auditoría y Logs
- Historial completo de actividades
- Filtros por fecha, empleado, tipo
- Exportación de logs
- Detalles de cada evento

### 📈 Reportes
- Generación de reportes personalizados
- Múltiples formatos: PDF, CSV, Excel
- Estadísticas visuales
- Descarga de reportes históricos

## 🔐 Autenticación

El sistema utiliza JWT para autenticación:
- Login con username/password
- Token almacenado en localStorage
- Renovación automática
- Logout con limpieza de sesión

## 📱 Responsive Design

- Sidebar colapsible en móviles
- Tablas con scroll horizontal
- Modales adaptables
- Touch-friendly

## 🎨 Personalización

### CSS Variables
El archivo `main.css` define variables CSS personalizables:
```css
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  /* ... más variables */
}
```

### Temas
Soporte básico para modo claro/oscuro mediante CSS variables.

## 🚀 Despliegue

### Integración con FastAPI
1. Construir el frontend: `npm run build`
2. Copiar archivos a `../www/admin/`
3. FastAPI servirá automáticamente desde `/admin`

### Acceso
Una vez desplegado, el panel estará disponible en:
`http://localhost:8081/admin/`

## 🛠️ Desarrollo

### Comandos útiles
```bash
# Desarrollo
npm run dev

# Construcción
npm run build

# Vista previa de construcción
npm run preview

# Construcción y copia automática
npm run build:prod
```

### Estructura de Componentes
- **Layout.vue**: Sidebar + header + content area
- **Vistas**: Una por cada sección principal
- **Composables**: Lógica reutilizable para API calls
- **Store**: Estado global con Pinia

### API Integration
Todas las peticiones API se realizan a través de composables que utilizan axios con interceptores para:
- Autenticación automática (JWT)
- Manejo de errores
- Redirección en caso de token expirado

## 📚 Tecnologías Utilizadas

- **Vue.js 3**: Framework principal
- **Vite**: Build tool y servidor de desarrollo
- **Vue Router**: Navegación SPA
- **Pinia**: Estado global
- **Axios**: Cliente HTTP
- **Chart.js**: Gráficos y estadísticas
- **Vue Toastification**: Notificaciones
- **Date-fns**: Manejo de fechas

## 🤝 Contribución

1. Seguir la estructura de archivos establecida
2. Usar composables para lógica de API
3. Mantener consistencia en el diseño
4. Documentar componentes complejos

## 📄 Licencia

Este proyecto es parte del sistema de reconocimiento facial de empleados.