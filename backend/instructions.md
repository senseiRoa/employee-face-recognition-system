
**Rol:**
Desarrollador experto en **Python** y **FastAPI**.

**Tareas a realizar:**

1. Lee el archivo `main.py` y organiza el proyecto en las siguientes carpetas, separando el código por responsabilidad:

   * `controllers` → para los endpoints (routers).
   * `services` → para la lógica de negocio.
   * `models` → para los modelos de base de datos (SQLAlchemy).
   * `helpers` → para funciones de apoyo (ej. hashing, validaciones).
   * `utils` → para utilidades generales (ej. JWT, manejo de fechas).

2. Refactoriza los **modelos de base de datos** para que:

   * Todos los IDs sean **numéricos y autoincrementales** (`Integer, primary_key=True, autoincrement=True`).

3. No ejecutes migraciones.

4. No instales dependencias nuevas (usar solo las ya disponibles).

5. No uses Git ni comandos relacionados con control de versiones.

6. Agrega nuevas tablas a la base de datos todo en ingles:

   * **Company** → con `id, nombre, usuario, contraseña`.
   * **LogsLogin** → con `id, company_id, fecha, ubicación, navegador`.

7. Implementa funcionalidad para manejar **tokens JWT** a partir de `Company`:

   * Crear token.
   * Validar token.
   * Refrescar token.
   * Revocar token.

8. Implementa la lógica de **sesiones**:

   * Login.
   * Logout.
   * Refresh.

9. Mejora los endpoints para que tengan **lógica por dominio** (ej. `/company`, `/auth`, `/logs`).

10. Asegura que todos los endpoints requieran un **JWT válido** para poder acceder.
11. genera un readme.md en ingles con toda la descripcion tecnica del proyecto , adicionando informacion de como se organiza las clases, la funcionalidad de cada una, etc

12. Genera un **RouteMap en forma de TODO list** con los endpoints y marca el progreso de implementación.

