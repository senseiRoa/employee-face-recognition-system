
# Guía Docker - Employee Backend

Este documento describe cómo ejecutar, detener, actualizar y administrar la aplicación **Employee Backend** utilizando Docker y Docker Compose.  
La aplicación utiliza **SQLite** como base de datos, persistida en la carpeta `./data`.

---

## 📦 Requisitos previos

- Tener instalado [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/).
- Clonar este repositorio y ubicarse en el directorio raíz donde está el archivo `docker-compose.yml`.

---

## ▶️ Levantar la aplicación

Construir la imagen y levantar el contenedor:

```bash
docker-compose up -d --build
````

* `-d` → Ejecuta en segundo plano (modo *detached*).
* `--build` → Reconstruye la imagen en caso de que el código haya cambiado.

La API quedará disponible en:
👉 [http://localhost:8081](http://localhost:8081)

---

## ⏹️ Detener la aplicación

Detener los contenedores:

```bash
docker-compose down
```

Esto **detiene y elimina** el contenedor, pero los datos se mantienen en la carpeta `./data`.

---

## 🔄 Actualizar la aplicación

Si hiciste cambios en el código o en el Dockerfile:

```bash
docker-compose build
docker-compose up -d
```

O en un solo paso:

```bash
docker-compose up -d --build
```

---

## 🗄️ Verificar la base de datos SQLite

La base de datos se guarda en `./data/`.
Puedes inspeccionarla entrando al contenedor y usando `sqlite3`:

```bash
docker exec -it employee-backend sh
```

Dentro del contenedor:

```bash
sqlite3 /app/data/employee.db
```

Comandos útiles en SQLite:

```sql
.tables;              -- Ver todas las tablas
.schema employees;    -- Ver la estructura de la tabla employees
SELECT * FROM employees LIMIT 5;   -- Ver registros
.exit                 -- Salir
```

---

## 📜 Logs de la aplicación

Para ver los logs en tiempo real:

```bash
docker logs -f employee-backend
```

---

## 🧪 Ejecutar pruebas (unittest)

Si tienes pruebas en la carpeta `tests/`, puedes correrlas dentro del contenedor:

```bash
docker-compose run --rm api python -m unittest discover tests
```

---

## ♻️ Limpiar recursos

Eliminar contenedores, red y volúmenes anónimos:

```bash
docker-compose down -v
```

⚠️ Ojo: esto borrará también los datos de la base de datos si no están montados en `./data`.

---

## 📂 Persistencia de datos

* La base de datos se encuentra en el volumen montado `./data:/app/data`.
* Esto significa que los datos se mantienen incluso si el contenedor se elimina o se vuelve a crear.
