# Plan de Acción - Refactorización de Reconocimiento Facial

## Backend

- [x] **Arquitectura Hexagonal**: Estructura de directorios creada (dominio, aplicación, infraestructura).
- [x] **Base de Datos**: Configurar MySQL en `docker-compose.yml` y usar SQLAlchemy con Alembic.
- [x] **Autenticación**: Implementar validación de JWT con endpoint `/connect/introspect`.
- [x] **Reconocimiento Facial**: Sustituir `dlib/face_recognition` por `deepface`.

## Frontend

- [x] **Integración**: Asegurar que el frontend Angular/Ionic se integre sin cambios mayores.

## Pruebas

- [x] **Scripts cURL**: Generar scripts de prueba para los endpoints.

## Documentación

- [x] **Markdown**: Crear documentación con setup, comandos y endpoints.
