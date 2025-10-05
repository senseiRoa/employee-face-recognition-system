# 🚀 Guía de Desarrollo - admin-panel Vue.js

## 📋 Resumen

Este admin-panel se puede ejecutar de **2 maneras diferentes** según el flujo de trabajo que prefieras:

## 🔥 Opción 1: Desarrollo Completo (RECOMENDADO)

### ✅ Ventajas
- **Hot Reload**: Cambios instantáneos sin recargar página
- **Vue DevTools**: Debugging avanzado
- **Source Maps**: Debugging de código fuente
- **Mejor performance**: Sin compilación en cada cambio
- **API Proxy**: Conecta automáticamente al backend

### 🚀 Cómo usar

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload

# Terminal 2: admin-panel 
cd admin-panel
npm run dev
```

### 📍 URLs
- **admin-panel (desarrollo)**: http://localhost:3000 (o el puerto que muestre Vite)
- **Backend API**: http://localhost:8081
- **Proxy automático**: Todas las llamadas API se redirigen automáticamente

---

## 🏭 Opción 2: Integración Completa

### ✅ Ventajas
- **Comportamiento de producción**: Igual al servidor real
- **Testing final**: Prueba la integración completa
- **Un solo puerto**: Todo desde http://localhost:8081

### 🚀 Cómo usar

```bash
# Desde el directorio admin-panel
npm run build:prod

# El panel estará disponible en:
# http://localhost:8081/admin/
```

---

## 🔧 Configuración Automática

El proyecto está configurado para detectar automáticamente el entorno:

| Modo | Base URL | Proxy | Hot Reload |
|------|----------|-------|------------|
| `npm run dev` | `/` | ✅ Auto | ✅ Sí |
| `npm run build` | `/admin/` | ❌ No | ❌ No |

---

## 📚 Comandos Disponibles

```bash
# Desarrollo con hot reload
npm run dev

# Construcción para producción
npm run build

# Construcción + copia automática al backend
npm run build:prod

# Vista previa de la build
npm run preview

# Solo limpiar y copiar archivos
npm run copy-to-www
```

---

## 🛠️ Estructura del Proyecto

```
admin-panel/
├── src/
│   ├── components/       # Componentes reutilizables
│   ├── composables/      # Lógica de API y hooks
│   ├── router/           # Configuración de rutas
│   ├── store/            # Estado global (Pinia)
│   ├── views/            # Páginas principales
│   └── assets/           # CSS y recursos
├── public/               # Archivos estáticos
├── dist/                 # Build de producción
├── vite.config.js        # Configuración de Vite
└── package.json          # Dependencias y scripts
```

---

## 🔗 API Integration

### Proxy de Desarrollo
El `vite.config.js` incluye proxy automático para todas las rutas API:

```javascript
proxy: {
  '/auth': 'http://localhost:8081',
  '/companies': 'http://localhost:8081',
  '/warehouses': 'http://localhost:8081',
  '/employees': 'http://localhost:8081',
  // ... más rutas
}
```

### Composables API
Utiliza los composables para hacer llamadas API:

```javascript
// Ejemplo en una vista
import { useCompanies } from '@/composables/useCompanies'

const { companies, loading, error, fetchCompanies } = useCompanies()
```

---

## 🎯 Mejores Prácticas

### Para Desarrollo Activo
1. **Usa `npm run dev`** para desarrollo diario
2. **Mantén el backend ejecutándose** en paralelo
3. **Instala Vue DevTools** en tu navegador
4. **Revisa la consola** para errores de API

### Para Testing Final
1. **Usa `npm run build:prod`** antes de commit
2. **Prueba en http://localhost:8081/admin/** 
3. **Verifica que todas las funciones trabajen**

### Para Producción
1. **Ejecuta `npm run build`** para optimizar
2. **Los archivos van a `dist/`**
3. **Se copian automáticamente a `../www/admin/`**

---

## 🔍 Troubleshooting

### ❌ "Puerto en uso"
```bash
# Vite automáticamente busca el siguiente puerto disponible
# Fíjate en la consola cuál puerto asignó
```

### ❌ "API calls fallan"
```bash
# Verifica que el backend esté ejecutándose en puerto 8081
curl http://localhost:8081/health
```

### ❌ "Hot reload no funciona"
```bash
# Reinicia el servidor de desarrollo
npm run dev
```

### ❌ "Cambios no se ven en /admin/"
```bash
# Necesitas rebuild para integración
npm run build:prod
```

---

## 🚀 Flujo de Trabajo Recomendado

1. **Inicio de día**: 
   ```bash
   # Terminal 1
   cd backend && python -m uvicorn main:app --reload
   
   # Terminal 2  
   cd admin-panel && npm run dev
   ```

2. **Desarrollo**: Trabaja en http://localhost:3002/ (o el puerto asignado)

3. **Testing final**: `npm run build:prod` y prueba en http://localhost:8081/admin/

4. **Commit**: Asegúrate de que ambos modos funcionen

---

## 📧 Contacto

Si tienes problemas o dudas sobre el setup de desarrollo, contacta al equipo técnico.