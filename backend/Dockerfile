# Multi-stage build for Employee Face Recognition System
# Stage 1: Build admin-panel (Vue.js frontend)
FROM node:18-alpine AS frontend-builder

WORKDIR /app/admin-panel

# Copy package files for dependency installation
COPY admin-panel/package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy admin-panel source code and build
COPY admin-panel/ ./
RUN npm run build

# Stage 2: Python backend with integrated frontend
FROM python:3.11-bullseye AS backend

# Install system dependencies for dlib/face_recognition
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/admin-panel/dist ./www/admin

# Create necessary directories
RUN mkdir -p /app/data /app/uploads /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8081/health')" || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]