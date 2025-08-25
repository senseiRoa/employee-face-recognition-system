

# 📱 Employee Face Recognition App

Aplicación híbrida desarrollada con **Ionic + Angular + Capacitor** para el registro y validación de empleados mediante reconocimiento facial.
El backend está construido en **FastAPI (Python)** y desplegado en **Docker**.

---

## 🚀 Características principales

* Registro de ingreso de empleados mediante captura de foto desde la cámara del dispositivo.
* Envío de la imagen al backend en **FastAPI** para la validación de identidad.
* Integración con librería de **Face Recognition en Python**.
* Despliegue del backend en contenedores **Docker**.
* Comunicación con el backend a través de **API REST**.
* Aplicación híbrida: funciona en **Android, iOS y Web**.

---

## 🛠️ Tecnologías utilizadas

### Frontend (Móvil/Web)

* [Ionic Framework](https://ionicframework.com/) (Angular + Capacitor)
* [Capacitor Camera](https://capacitorjs.com/docs/apis/camera) para captura de fotos
* Angular 12

### Backend

* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [Face Recognition](https://github.com/ageitgey/face_recognition) (Python lib)
* [Docker](https://www.docker.com/)

---

## 📂 Estructura del proyecto

```
face_recognition_test/
│
├── backend/                  # API con FastAPI
│   ├── main.py                # Punto de entrada FastAPI
│   ├── requirements.txt       # Dependencias backend
│   └── Dockerfile             # Imagen Docker para backend
│
├── frontend/                  # App Ionic + Angular
│   ├── src/                   # Código fuente de Ionic
│   ├── capacitor.config.ts    # Configuración Capacitor
│   └── package.json           # Dependencias frontend
│
└── README.md
```

---

## ⚡ Instalación y uso

### 🔹 Backend

1. Clonar repositorio

   ```bash
   git clone https://github.com/tu-usuario/face_recognition_test.git
   cd face_recognition_test/backend
   ```

2. Crear entorno virtual e instalar dependencias

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # Linux/Mac

   pip install -r requirements.txt
   ```

3. Ejecutar el servidor FastAPI

   ```bash
   uvicorn main:app --reload --port 8001
   ```

4. Probar en [http://localhost:8001/docs](http://localhost:8001/docs)

---

### 🔹 Frontend (Ionic)

1. Ir a la carpeta del frontend

   ```bash
   cd face_recognition_test/frontend
   ```

2. Instalar dependencias

   ```bash
   npm install
   ```

3. Levantar la app en modo desarrollo

   ```bash
   ionic serve
   ```

4. Probar en dispositivo físico

   ```bash
   ionic capacitor run android
   ionic capacitor run ios
   ```

---

## 🧪 Pruebas

* Probar con distintos usuarios registrados en el backend.
* Validar coincidencias y rechazos en la API de reconocimiento.
* Revisar logs en consola de backend y frontend.

---

## 📌 Pendientes / Roadmap

* [ ] Manejo de múltiples rostros por empleado
* [ ] Notificaciones push al validar ingreso
* [ ] Persistencia de registros en base de datos SQL
* [ ] Despliegue automático con GitHub Actions + Docker

---



## ⚠️ Problemas comunes en compilación Android (Ionic/Capacitor)

### 1. Versión de **Java (JDK)**

* El **Android Gradle Plugin (AGP)** requiere **Java 17** o superior.
* Si ves un error como:

  ```
  Android Gradle plugin requires Java 17 to run. You are currently using Java 11.
  ```

  significa que tu `JAVA_HOME` apunta a una versión incorrecta.

**Solución:**

1. Instalar [JDK 17](https://adoptium.net/temurin/releases/?version=17).
2. Configurar `JAVA_HOME` en Windows (ejemplo):

   ```
   C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot
   ```

3. Verificar instalación:

   ```sh
   java -version
   ```

---

### 2. Compatibilidad de **Android Studio y AGP**

Si aparece un error como:

```
The project is using an incompatible version (AGP 8.7.2) of the Android Gradle plugin.
Latest supported version is AGP 8.3.1
```

Significa que tu Android Studio no soporta esa versión de **AGP**.

**Opciones de solución:**

* **Actualizar Android Studio** a la última versión.
* O **ajustar el AGP** en tu proyecto:

  * En `android/build.gradle` cambiar:

    ```gradle
    classpath 'com.android.tools.build:gradle:8.7.2'
    ```

    por:

    ```gradle
    classpath 'com.android.tools.build:gradle:8.3.1'
    ```

  * En `android/gradle/wrapper/gradle-wrapper.properties` ajustar:

    ```properties
    distributionUrl=https\://services.gradle.org/distributions/gradle-8.4-all.zip
    ```

---

### 3. Comandos útiles de Capacitor

#### Crear plataforma Android

```sh
ionic capacitor add android
```

#### Sincronizar cambios de Ionic/Angular con el proyecto Android

```sh
ionic capacitor sync android
```

#### Ejecutar en emulador/dispositivo

```sh
ionic capacitor run android
```

#### Abrir proyecto en Android Studio

```sh
ionic capacitor open android
```

#### Limpiar compilaciones

```sh
cd android
gradlew clean
```

