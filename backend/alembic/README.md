# 📦 Migraciones de Base de Datos con Alembic

Este proyecto usa **[Alembic](https://alembic.sqlalchemy.org/)** para manejar migraciones de la base de datos MySQL (`timeTrackerDB`).

---

## ⚙️ Requisitos

1. Tener **Python 3.11+** instalado.
2. Instalar dependencias desde `requirements.txt`:

```bash
   pip install -r requirements.txt
````

Incluye `alembic` y `mysqlclient`.

3. Configurar la URL de la base de datos en `alembic.ini` o en tu variable de entorno:

   ```
   sqlachemy.url = mysql+mysqldb://root:password@host.docker.internal:3307/timeTrackerDB
   ```

---

## 📂 Estructura de Migraciones

La carpeta generada por Alembic contiene:

```
alembic/
  env.py
  script.py.mako   # plantilla para nuevas migraciones
  versions/        # aquí se guardan las migraciones generadas
alembic.ini
```

* `env.py` → Configuración del contexto y la conexión a la BD.
* `script.py.mako` → Plantilla base para nuevas migraciones.
* `versions/` → Migraciones versionadas (una por cada cambio de schema).

---

## 🚀 Flujo de Trabajo

### 1️⃣ Crear una nueva migración

Ejecutar:

```bash
alembic revision -m --autogenerate "descripcion de la migracion"
```

Esto creará un archivo dentro de `alembic/versions/` con un ID único.
Ejemplo: `20251002_abcd1234_create_users_table.py`.

---

### 2️⃣ Editar la migración

Abrir el archivo en `alembic/versions/` y definir los cambios en las funciones:

```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('users')
```

---

### 3️⃣ Aplicar la migración

Para llevar la base de datos al último estado:

```bash
alembic upgrade head
```

---

### 4️⃣ Revertir migración

Para deshacer la última migración:

```bash
alembic downgrade -1
```

---

### 5️⃣ Ver el historial de migraciones

```bash
alembic history
```

---

### 6️⃣ Comprobar estado actual

```bash
alembic current
```

---

## 📝 Notas

* Alembic crea y mantiene la tabla **`alembic_version`** en la base de datos, donde guarda la versión actual del esquema.
* Siempre valida tu conexión MySQL antes de ejecutar migraciones.
* Si trabajas con múltiples ramas de código, recuerda que **las migraciones deben mantenerse sincronizadas** para evitar conflictos.

---

👨‍💻 **Ejemplo rápido**

```bash
# crear migración inicial
alembic revision -m "create users table"

# editar la migración y definir la tabla

# aplicar a la base
alembic upgrade head
```
