
# POC - Employee Face Recognition System

## 📌 Descripción

Este proyecto es una **Prueba de Concepto (POC)** que permite el registro y validación de empleados mediante **reconocimiento facial**.
La aplicación consta de dos partes principales:

* **Frontend**: Construido con **Angular 18 + Ionic + Capacitor**, permite capturar la foto del empleado utilizando la cámara del dispositivo.
* **Backend**: Desarrollado en **Python (FastAPI)**, recibe la imagen, realiza la comparación facial y registra el acceso del empleado en una base de datos.

El backend está preparado para ejecutarse en **Docker**, facilitando su despliegue en entornos de prueba.

---

## 🛠️ Tecnologías utilizadas

### Frontend

* Angular 18 (Standalone Components)
* Ionic Framework + Capacitor
* TypeScript

### Backend

* Python 3.11+
* FastAPI
* face\_recognition (dlib)
* SQLite (para almacenamiento de prueba)
* Docker

---

## 🚀 Instalación y ejecución

### 🔹 Frontend (Angular + Ionic)

```bash
# Clonar el proyecto
git clone https://github.com/senseiRoa/face_recognition_test.git
cd TU-REPO/frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
ionic serve
```

### 🔹 Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # En Linux/Mac
venv\Scripts\activate      # En Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar backend
uvicorn main:app --reload
```

Acceso a la API: 👉 [http://localhost:8081/docs](http://localhost:8081/docs)

---

## 🧪 Flujo de la POC

1. El empleado se registra en la app con sus datos básicos.
2. La aplicación móvil toma una foto con la cámara.
3. La imagen se envía al backend en FastAPI.
4. El backend compara la foto con la base de datos de empleados.
5. Si coincide, se registra la entrada del empleado.

---

## 📦 Despliegue con Docker (Backend)

```bash
cd backend
docker build -t face-recognition-api .
docker run -d -p 8081:8081 face-recognition-api
```

---

## 📌 Próximos pasos

* Implementar validación de múltiples empleados.
* Integrar notificaciones de acceso.
* Conectar a una base de datos corporativa.

---

## 📄 Licencia

Este proyecto se desarrolla únicamente como **Prueba de Concepto (POC)** y no está destinado a uso en producción.

