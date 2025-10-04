
# 🐳 Desarrollo con Dev Containers (VS Code)

Este proyecto utiliza **Dev Containers** de VS Code para asegurar un entorno de desarrollo consistente y evitar problemas de dependencias nativas, especialmente con **dlib** (librería utilizada en `face_recognition`).

En **Windows**, la instalación de `dlib` y dependencias de compilación puede ser compleja.  
Por eso, el desarrollo se realiza dentro de un contenedor **Docker** que ya incluye todas las librerías necesarias.

---

## 🚀 ¿Por qué usar un Dev Container?

- **Compatibilidad**: `dlib` y librerías de compilación funcionan correctamente en Linux dentro del contenedor.
- **Portabilidad**: Cualquier desarrollador puede clonar el repo y trabajar sin preocuparse por configuraciones locales.
- **Consistencia**: Todos usamos la misma versión de Python, dependencias y sistema base.

---

## 📂 Configuración del Dev Container

El proyecto incluye:

- `.devcontainer/devcontainer.json` → configuración principal del contenedor.
- `.devcontainer/Dockerfile` → imagen basada en `python:3.11-bullseye` con dependencias (`build-essential`, `cmake`, `libopenblas-dev`, `liblapack-dev`, etc).
- Montaje del código en `/workspaces/face_recognition_test`.

---

## ▶️ Cómo iniciar el entorno

1. Instalar:
   - [Docker Desktop](https://www.docker.com/products/docker-desktop)  
   - [Visual Studio Code](https://code.visualstudio.com/)  
   - [Extensión Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)  

2. Abrir el proyecto en VS Code.

3. En la barra inferior, hacer clic en **"Reopen in Container"**.  
   > Esto construirá la imagen y montará el entorno de desarrollo.

4. Una vez abierto el contenedor, ya puedes correr Python, instalar paquetes adicionales y usar las tareas configuradas.

---

## 📌 Uso de Tasks en VS Code

Este proyecto define **tareas (`tasks.json`)** para simplificar comandos frecuentes.

Ejemplos de tasks disponibles:

- **Run Backend** → Levanta el servidor FastAPI con `uvicorn`.
- **Alembic Migration** → Crea/aplica migraciones de base de datos.
- **Debug Backend** → Ejecuta el backend con soporte de depuración.

👉 Para ejecutarlas:  
Presiona `Ctrl+Shift+P` → **"Run Task"** → selecciona la tarea.

---

## 🐞 Debug en VS Code

El contenedor está configurado para permitir **debug remoto** con `debugpy`.

1. Ve a la pestaña **Run and Debug** en VS Code.
2. Selecciona **"Python: FastAPI (devcontainer)"**.
3. El backend se iniciará en modo debug, permitiéndote usar breakpoints.

---

## 🗄️ Base de datos MySQL

Para desarrollo local, se usa un contenedor MySQL separado.  
Ejemplo de ejecución:

```bash
docker run --name oagtech21-mysql-db \
  -e MYSQL_ROOT_PASSWORD=secret123 \
  -e MYSQL_DATABASE=timeTrackerDB \
  -e MYSQL_USER=test \
  -e MYSQL_PASSWORD=test123 \
  -p 3307:3306 \
  -d mysql:8.0
````

Conexión en SQLAlchemy (usando `mysqlclient`):

```
mysql+mysqldb://root:secret123@host.docker.internal:3307/timeTrackerDB
```

---

## 📚 Flujo recomendado de trabajo

1. Levantar el Dev Container en VS Code.
2. Levantar MySQL con Docker (si no está corriendo).
3. Ejecutar migraciones con Alembic usando un **task**.
4. Ejecutar el backend con el task **Run Backend**.
5. Usar **Debug Backend** si necesitas inspeccionar código.

---

✅ Con este enfoque, el entorno de desarrollo es reproducible en cualquier máquina, sin problemas de dependencias nativas como ocurre en Windows con `dlib`.




> Una vez iniciado el entorno de desarrollo, la aplicación estará disponible desde cualquier navegador en la siguiente URL:
> **[http://localhost:8081/health](http://localhost:8081/health)**
>
> Esta ruta de verificación (`/health`) permite comprobar que el backend está en ejecución correctamente.


