FROM python:3.11-bullseye
# Dependencias de compilación para dlib/face_recognition
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential cmake libopenblas-dev liblapack-dev libjpeg-dev \
&& rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt
COPY . .
# Crear carpeta de datos para SQLite
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]