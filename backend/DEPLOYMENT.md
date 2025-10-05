# 🚀 Quick Deployment Guide

## Prerequisites Built Image

Before deploying, ensure you have built the Docker image using our build process:

```bash
# From project root
./backend/scripts/build-docker.sh -t v1.0.0 -p
```

## 🐋 Docker Run (Simple)

```bash
# Basic run
docker run -d \
  --name face-recognition-app \
  -p 8081:8081 \
  -e DB_HOST=localhost \
  -e DB_USER=root \
  -e DB_PASSWORD=m634kkkd/* \
  -e DB_DATABASE=timeTrackerDB \
  -e DB_PORT=3307 \
  -e JWT_SECRET_KEY=8f7b2c1e5d9a4e6f3b7c0d2a6e1f4b8c \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=1440 \
  steelerp.azurecr.io/face_recognition_backend:latest
```

## 🐙 Docker Compose (Recommended)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  app:
    image: steelerp.azurecr.io/face_recognition_backend:latest
    container_name: face-recognition-app
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_DATABASE=employee_tracker
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - CORS_ORIGINS=["https://yourdomain.com"]
    depends_on:
      mysql:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8081/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  mysql:
    image: mysql:8.0
    container_name: face-recognition-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: employee_tracker
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

volumes:
  mysql_data:
```

Create `.env` file:
```env
DB_USER=produser
DB_PASSWORD=secure_password_here
DB_ROOT_PASSWORD=secure_root_password_here
JWT_SECRET_KEY=secure_jwt_secret_key_minimum_32_characters
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 Access Points

- **API Documentation**: http://your-server:8081/docs
- **Admin Panel**: http://your-server:8081/admin/
- **Health Check**: http://your-server:8081/health

## 🔒 Production Security

1. **Change default passwords**
2. **Use HTTPS in production**
3. **Configure firewall rules**
4. **Set up SSL certificates**
5. **Enable backup strategy**