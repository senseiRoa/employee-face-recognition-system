
Quiero que actúes como **desarrollador fullstack senior especializado en Python** y tu tarea es **refactorizar y robustecer** un proyecto existente de reconocimiento facial.

### 🎯 Requerimientos del nuevo stack

1. **Backend**

   * Lenguaje: Python 3.11+
   * Framework: FastAPI
   * Arquitectura: Hexagonal (puertos y adaptadores) para facilitar mantenimiento y escalabilidad.
   * Autenticación: Validación de JWT con endpoint `/connect/introspect`, por ejemplo:

     ```bash
     curl --location '/connect/introspect' \
       --header 'Authorization: Basic RVNEQVZBUElSZXNvdXJjZTpwcnVlYmFkZWZ1ZWdv' \
       --form 'token="eyJPI-GNUoMRP7HjnCw"'
     ```

   * Base de datos: MySQL 8 (con SQLAlchemy + Alembic para migraciones).
   * Contenedores: Docker + docker-compose.

2. **Reconocimiento facial**

   * Sustituir dependencia `dlib/face_recognition` por una librería más robusta, moderna y mantenida (ejemplo: `deepface`, `insightface`, o `mediapipe` de Google).
   * Mantener endpoints equivalentes a los actuales: `/register_face`, `/check_in_out`, `/employees`, `/logs`.

3. **Frontend**

   * Angular/Ionic existente debe poder integrarse sin cambios mayores.
   * Backend debe respetar los contratos actuales de API, pero mejorar la seguridad (ej: tokens, validación de roles).

4. **Pruebas**

   * Tests unitarios y de integración (pytest).
   * Scripts cURL de prueba para endpoints.

### 🛠️ Expectativa de entrega

* Código refactorizado con estructura clara de **dominio, infraestructura y aplicación** (arquitectura hexagonal).
* Configuración de MySQL en `docker-compose.yml`.
* Implementación del flujo de introspección de JWT.
* Ejemplos de endpoints actualizados con seguridad.
* Documentación breve en Markdown con:

  * Setup del entorno
  * Comandos para correr tests
  * Endpoints disponibles

