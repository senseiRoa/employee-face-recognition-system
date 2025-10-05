# 🐳 Docker Build & Deployment Guide

This guide explains how to build and deploy the complete Employee Face Recognition System using Docker. The build process includes both the Vue.js admin panel and the FastAPI backend in a single, optimized container.

## 🏗️ Build Architecture

The Docker build uses a **multi-stage approach** to create an optimized final image:

```
┌─────────────────┐    ┌─────────────────┐
│   Stage 1:      │    │   Stage 2:      │
│ Frontend Build  │───▶│ Backend + UI    │
│ (Node.js)       │    │ (Python)        │
│                 │    │                 │
│ • Build Vue.js  │    │ • FastAPI       │
│ • Optimize      │    │ • Built frontend│
│ • Create dist/  │    │ • Final image   │
└─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Git** for cloning the repository
- **4GB+ free disk space** for build process
- **Internet connection** for downloading dependencies

## 🚀 Quick Build & Deploy

### Option 1: Automated Build Script (Recommended)

```bash
# From project root directory
./backend/scripts/build-docker.sh

# Or on Windows
backend\scripts\build-docker.bat
```

### Option 2: Manual Build Commands

```bash
# Navigate to project root (important!)
cd /path/to/employee-face-recognition-system

# Build the complete image
docker build -f backend/Dockerfile -t face-recognition-system:latest .

# Run the container
docker run -d \
  --name face-recognition-app \
  -p 8081:8081 \
  -e DB_HOST=your-db-host \
  -e DB_USER=your-db-user \
  -e DB_PASSWORD=your-db-password \
  face-recognition-system:latest
```

## 🏷️ Registry Deployment

### Build for Azure Container Registry

```bash
# Build with ACR tag
docker build -f backend/Dockerfile \
  -t steelerp.azurecr.io/face_recognition_backend:latest \
  -t steelerp.azurecr.io/face_recognition_backend:$(date +%Y%m%d-%H%M%S) \
  .

# Login to Azure Container Registry
az acr login --name steelerp

# Push to registry
docker push steelerp.azurecr.io/face_recognition_backend:latest
docker push steelerp.azurecr.io/face_recognition_backend:$(date +%Y%m%d-%H%M%S)
```

### Build for Docker Hub

```bash
# Build with Docker Hub tag
docker build -f backend/Dockerfile \
  -t your-username/face-recognition-system:latest \
  -t your-username/face-recognition-system:v1.0.0 \
  .

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push your-username/face-recognition-system:latest
docker push your-username/face-recognition-system:v1.0.0
```

## 📁 Build Context & File Structure

The build expects the following structure:

```
employee-face-recognition-system/
├── admin-panel/              # Vue.js frontend source
│   ├── package.json
│   ├── src/
│   └── dist/                 # Generated during build
├── backend/                  # FastAPI backend
│   ├── Dockerfile            # Multi-stage build file
│   ├── requirements.txt
│   ├── main.py
│   └── www/admin/           # Frontend files copied here
└── docker-compose.yml
```

## ⚙️ Build Process Details

### Stage 1: Frontend Build (Node.js)
1. **Base Image**: `node:18-alpine` (lightweight)
2. **Install Dependencies**: `npm ci --only=production`
3. **Build Process**: `npm run build`
4. **Output**: Optimized static files in `/dist`

### Stage 2: Backend Integration (Python)
1. **Base Image**: `python:3.11-bullseye`
2. **System Dependencies**: dlib, OpenCV, face_recognition requirements
3. **Python Dependencies**: FastAPI, SQLAlchemy, etc.
4. **Frontend Integration**: Copy built files to `www/admin/`
5. **Security**: Non-root user, health checks
6. **Optimization**: Multi-layer caching, minimal final size

## 🔧 Build Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | Database hostname | localhost | Yes |
| `DB_PORT` | Database port | 3306 | No |
| `DB_USER` | Database username | - | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `DB_DATABASE` | Database name | employee_tracker | No |
| `JWT_SECRET_KEY` | JWT secret | - | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | ["*"] | No |

### Build Arguments

```bash
# Custom build with arguments
docker build -f backend/Dockerfile \
  --build-arg NODE_VERSION=18 \
  --build-arg PYTHON_VERSION=3.11 \
  -t face-recognition-system:custom \
  .
```

## 🐋 Docker Compose Deployment

### Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8081:8081"
    environment:
      - DB_HOST=mysql
      - DB_USER=devuser
      - DB_PASSWORD=devpass
    depends_on:
      - mysql
  
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_DATABASE=employee_tracker
```

### Production Environment

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    image: steelerp.azurecr.io/face_recognition_backend:latest
    ports:
      - "8081:8081"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔍 Build Verification

### Check Build Success

```bash
# Verify image was created
docker images | grep face-recognition

# Check image size
docker image inspect face-recognition-system:latest --format='{{.Size}}'

# Test run locally
docker run --rm -p 8081:8081 face-recognition-system:latest
```

### Verify Application

```bash
# Health check
curl http://localhost:8081/health

# API documentation
curl http://localhost:8081/docs

# Admin panel
curl http://localhost:8081/admin/
```

## 🚨 Troubleshooting

### Common Build Issues

**Problem**: Frontend build fails
```bash
# Solution: Check Node.js version and dependencies
docker build --no-cache --progress=plain -f backend/Dockerfile .
```

**Problem**: Python dependencies fail
```bash
# Solution: Check system dependencies
# Make sure build-essential, cmake are installed in Dockerfile
```

**Problem**: face_recognition takes too long to compile
```bash
# Solution: This is normal for first build (15-25 minutes)
# Use pre-built wheels if available:
# pip install --find-links https://wheels.galaxyproject.org/ dlib
```

**Problem**: Build runs out of memory
```bash
# Solution: Increase Docker memory limit to 4GB+
# Docker Desktop -> Settings -> Resources -> Memory
```

**Problem**: Permission denied errors
```bash
# Solution: Check file permissions
chmod +x backend/scripts/build-docker.sh
```

**Problem**: Large image size
```bash
# Solution: Use .dockerignore to exclude unnecessary files
# Check: node_modules, .git, .venv, __pycache__
```

### Performance Optimization

1. **Use .dockerignore** to exclude unnecessary files
2. **Multi-stage builds** to reduce final image size
3. **Layer caching** for faster rebuilds
4. **Alpine base images** where possible
5. **Pre-built wheels** for Python packages when available

### Build Time Optimization Tips

```bash
# Use BuildKit for better caching
export DOCKER_BUILDKIT=1

# Build with progress output to monitor stages
docker build --progress=plain -f backend/Dockerfile .

# Use build cache from registry
docker build --cache-from your-registry/cache-image:latest .
```

## 📊 Build Metrics

### Expected Build Times
- **First build**: 15-25 minutes (face_recognition compilation is intensive)
- **Incremental builds**: 2-5 minutes (with cache)
- **Final image size**: ~1.5-2GB (includes dlib, OpenCV, and dependencies)

### Resource Requirements
- **Build RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 5GB during build, 2GB final
- **CPU**: Multi-core recommended for faster builds
- **Time**: First build can take 20+ minutes due to dlib/face_recognition compilation

## 🔐 Security Considerations

### Production Security
- ✅ **Non-root user**: Application runs as `appuser`
- ✅ **Health checks**: Automatic container health monitoring
- ✅ **Minimal attack surface**: Only necessary packages installed
- ✅ **Environment variables**: Secrets managed externally
- ✅ **Regular updates**: Base images updated regularly

### Registry Security
- 🔒 **Private registries**: Use ACR or private Docker Hub
- 🔒 **Image scanning**: Enable vulnerability scanning
- 🔒 **Access control**: Limit push/pull permissions
- 🔒 **Tag management**: Use semantic versioning

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/develop/advanced-builds/multistage-build/)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Docker Hub](https://docs.docker.com/docker-hub/)

## 🤝 Contributing

When modifying the build process:

1. **Test locally** before pushing changes
2. **Update documentation** for any new requirements
3. **Maintain compatibility** with existing deployments
4. **Consider security implications** of any changes
5. **Optimize for build time** and image size

---

**📝 Note**: This build process creates a production-ready container with both frontend and backend integrated. For development, consider using the dev container setup instead.