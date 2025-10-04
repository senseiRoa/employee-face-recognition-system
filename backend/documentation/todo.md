# Plan de Ejecución y Progreso

Este documento detalla las tareas planificadas para la refactorización y mejora del proyecto de reconocimiento facial.

## Fase 1: Configuración y Análisis del Entorno
no ejecutes rquirements.txt por que localmente genera error ya eue estoy en windows, asume que este funciona bien
- [ ] Crear archivo `.env` para la gestión de secretos.
- [ ] Añadir `.env` al archivo `.gitignore`.
- [ ] Analizar y actualizar `requirements.txt` para Python 3.11.

## Fase 2: Integración de la Base de Datos (MySQL)

- [ ] Añadir servicio de MySQL 8 al `docker-compose.yml`.
- [ ] Configurar la conexión a la base de datos en `database.py` usando variables de entorno.
- [ ] Inicializar y configurar Alembic para las migraciones de la base de datos.
- [ ] Crear la migración inicial de los modelos existentes.

## Fase 3: Implementación de Autenticación (JWT Introspection)

- [ ] Crear un nuevo módulo de seguridad (`security.py`).
- [ ] Implementar la función de introspección de token que se comunique con el endpoint `/connect/introspect`.
- [ ] Crear una dependencia de FastAPI para proteger los endpoints.

## Fase 4: Refactorización y Robustecimiento

- [ ] Aplicar la dependencia de seguridad a los endpoints que lo requieran.
- [ ] Refactorizar el código para mejorar la claridad, el rendimiento y el manejo de errores.
- [ ] Actualizar el `README.md` con las nuevas instrucciones de configuración y uso.
- [ ] Proporcionar ejemplos de cómo consumir los endpoints seguros.

