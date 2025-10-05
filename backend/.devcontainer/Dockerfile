FROM python:3.11-bullseye

# Dependencias de compilación para dlib/face_recognition
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake libopenblas-dev liblapack-dev libjpeg-dev \
    git curl vim default-mysql-client\
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app


# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Crear carpeta de datos para SQLite
RUN mkdir -p /app/data

# Puerto de desarrollo
EXPOSE 8081

# Por defecto que se quede en shell (no ejecutar directamente uvicorn)
CMD [ "bash" ]
