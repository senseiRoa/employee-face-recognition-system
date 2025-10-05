# 🚀 Employee Face Recognition System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-brightgreen.svg)](https://vuejs.org/)
[![Ionic](https://img.shields.io/badge/Ionic-8.0-blue.svg)](https://ionicframework.com/)
[![Angular](https://img.shields.io/badge/Angular-20.0-red.svg)](https://angular.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📌 Overview

This is a complete **Employee Time Tracking System using Facial Recognition** built with modern technologies. The system provides a comprehensive solution for employee management, time tracking, and administration through facial biometric verification.

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🏗️ System Components](#️-system-components)
- [📁 Project Structure](#-project-structure)
- [📚 Documentation Index](#-documentation-index)
  - [🖥️ Admin Panel Documentation](#️-admin-panel-documentation)
  - [⚙️ Backend Documentation](#️-backend-documentation)
  - [📱 Mobile App Documentation](#-mobile-app-documentation)
  - [🐳 Docker & Deployment](#-docker--deployment)
  - [🧪 Testing Documentation](#-testing-documentation)
  - [🔐 Security Documentation](#-security-documentation)
- [📋 Prerequisites](#-prerequisites)
- [🎯 Key Features](#-key-features)
- [⚡ Quick Start Options](#-quick-start-options)
- [📞 Support & Contributing](#-support--contributing)

## 🚀 Quick Start

**🎉 New to the project?** Start here: **[📋 Complete Setup Guide](./GETTING_STARTED.md)**

| Component | Purpose | Technology | Quick Access |
|-----------|---------|------------|--------------|
| **Admin Panel** | Management dashboard | Vue.js 3 | <http://localhost:3031> |
| **Backend API** | Core services & Face Recognition | FastAPI + Python | <http://localhost:8081/docs> |
| **Employee App** | Mobile check-in/out | Ionic + Angular | <http://localhost:8100> |

## 🏗️ System Components

The application consists of three main components:

- **🖥️ Admin Panel** - Vue.js 3 web dashboard for comprehensive administration and analytics
- **⚙️ Backend** - FastAPI core with face recognition, JWT authentication, and MySQL database  
- **📱 Employee Register** - Ionic/Angular mobile app for tablets and smartphones

> **Note**: Only the backend currently supports Dev Container setup due to complex native dependencies (dlib, face_recognition).

## 📁 Project Structure

```
employee-face-recognition-system/
├── 🖥️ admin-panel/              # Vue.js 3 Admin Dashboard
│   ├── src/components/         # Reusable Vue components
│   ├── src/views/             # Page components
│   ├── scripts/               # Build and deployment scripts
│   └── package.json
│
├── ⚙️ backend/                  # FastAPI Core API
│   ├── controllers/           # API route handlers
│   ├── services/              # Business logic
│   ├── models/                # Database models
│   ├── tests/                 # Test suites
│   ├── documentation/         # Technical documentation
│   └── main.py
│
└── 📱 employee-register/        # Ionic/Angular Mobile App
    ├── src/app/               # Angular application
    ├── android/               # Android native project
    └── capacitor.config.ts
```

## 📚 Documentation Index

### 🖥️ Admin Panel Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Setup Guide** | Installation and development setup | [`admin-panel/README.md`](./admin-panel/README.md) |
| **Development Guide** | Development workflow and best practices | [`admin-panel/DEVELOPMENT_GUIDE.md`](./admin-panel/DEVELOPMENT_GUIDE.md) |
| **Build Scripts** | Frontend build and deployment automation | [`admin-panel/scripts/`](./admin-panel/scripts/) |

### ⚙️ Backend Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Quick Start** | Fast setup for backend development | [`backend/QUICK_START.md`](./backend/QUICK_START.md) |
| **Main README** | Backend overview and setup | [`backend/readme.md`](./backend/readme.md) |
| **Docker Build Guide** | Comprehensive Docker build documentation | [`backend/DOCKER_BUILD_GUIDE.md`](./backend/DOCKER_BUILD_GUIDE.md) |
| **Deployment Guide** | Production deployment instructions | [`backend/DEPLOYMENT.md`](./backend/DEPLOYMENT.md) |
| **Access Panel Guide** | Admin panel access configuration | [`backend/GUIA_ACCESO_PANEL.md`](./backend/GUIA_ACCESO_PANEL.md) |
| **API Documentation** | Interactive API docs (when running) | <http://localhost:8081/docs> |

#### Backend Technical Documentation

| Document | Description | Path |
|----------|-------------|------|
| **General Documentation** | Technical overview and architecture | [`backend/documentation/readme.md`](./backend/documentation/readme.md) |
| **Dev Container Guide** | VS Code development container setup | [`backend/documentation/README-dev-container.md`](./backend/documentation/README-dev-container.md) |
| **Docker Guide** | Docker development and deployment | [`backend/documentation/guia-docker.md`](./backend/documentation/guia-docker.md) |
| **Development TODO** | Pending tasks and improvements | [`backend/documentation/todo.md`](./backend/documentation/todo.md) |

### 📱 Mobile App Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Mobile App Setup** | Ionic/Angular app installation and setup | [`employee-register/readme.md`](./employee-register/readme.md) |

### 🐳 Docker & Deployment

| Document | Description | Path |
|----------|-------------|------|
| **Docker Build Guide** | Complete Docker build process documentation | [`backend/DOCKER_BUILD_GUIDE.md`](./backend/DOCKER_BUILD_GUIDE.md) |
| **Deployment Guide** | Production deployment strategies | [`backend/DEPLOYMENT.md`](./backend/DEPLOYMENT.md) |
| **Build Fix Summary** | Docker build troubleshooting and fixes | [`backend/BUILD_FIX_SUMMARY.md`](./backend/BUILD_FIX_SUMMARY.md) |
| **Dev Container Setup** | Development environment containerization | [`backend/documentation/README-dev-container.md`](./backend/documentation/README-dev-container.md) |

### 🧪 Testing Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Testing Guide** | Comprehensive testing setup and execution | [`backend/TESTING_GUIDE.md`](./backend/TESTING_GUIDE.md) |
| **Testing Summary** | Test results and coverage overview | [`backend/TESTING_SUMMARY.md`](./backend/TESTING_SUMMARY.md) |
| **Final Testing Summary** | Complete testing validation report | [`backend/TESTING_FINAL_SUMMARY.md`](./backend/TESTING_FINAL_SUMMARY.md) |
| **Database Migration** | Alembic database migration guide | [`backend/alembic/README.md`](./backend/alembic/README.md) |

### 🔐 Security Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Security Improvements** | Security enhancements and best practices | [`backend/SECURITY_IMPROVEMENTS.md`](./backend/SECURITY_IMPROVEMENTS.md) |

### 📋 Project Management

| Document | Description | Path |
|----------|-------------|------|
| **Project Steps** | Development milestones and progress | [`steps.md`](./steps.md) |
| **Steps PDF** | Downloadable project roadmap | [`steps.pdf`](./steps.pdf) |

## 📋 Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **VS Code** + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## �� Key Features

### ���️ Admin Panel (Vue.js 3)

- **Dashboard**: Real-time metrics and analytics
- **Employee Management**: Add, edit, view employees
- **Company Management**: Multi-tenant support
- **Access Logs**: View and export employee access history
- **User Management**: Admin user accounts and roles
- **Reports**: Generate PDF/CSV reports
- **Responsive Design**: Works on desktop and mobile

### ⚙️ Backend (FastAPI)

- **Face Recognition**: Using dlib and face_recognition library
- **JWT Authentication**: Secure API access
- **Multi-tenant**: Company-based data isolation
- **Database**: MySQL with SQLAlchemy ORM
- **API Documentation**: Automatic OpenAPI/Swagger docs
- **Testing**: Comprehensive test suite with pytest
- **Docker Ready**: Containerized for easy deployment

### 📱 Employee Mobile App (Ionic/Angular)

- **Photo Capture**: Native camera integration
- **Face Registration**: Register employee faces
- **Check-in/Check-out**: Automatic time tracking
- **Offline Support**: Works without internet connection
- **Cross-platform**: Android, iOS, and web
- **Real-time Sync**: Syncs with backend when online

## ⚡ Quick Start Options

### 🐳 Option 1: VS Code Dev Container (Recommended for Backend)

```bash
# 1. Open in VS Code
code .

# 2. Reopen in Container (Ctrl+Shift+P)
# Select: "Dev Containers: Reopen in Container"

# 3. Start backend inside container
cd backend && uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

### 🔧 Option 2: Manual Setup (All Components)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Admin Panel  
cd admin-panel
npm install && npm run dev

# Employee App
cd employee-register  
npm install && ionic serve
```

### 🐋 Option 3: Docker (Production-like)

```bash
# See complete Docker guide: backend/DOCKER_BUILD_GUIDE.md
docker build -t face-recognition-system .
docker run -p 8081:8081 face-recognition-system
# Access: http://localhost:8081
```

## 🚨 Important Notes

> **⚠️ Dev Container Support**: Only the backend currently supports VS Code Dev Container due to complex native dependencies (dlib, face_recognition library).

> **🔐 Security**: This is a Proof of Concept. For production use, implement proper security measures, HTTPS, and comply with data privacy regulations.

## 📞 Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/senseiRoa/employee-face-recognition-system/issues)
- **Contributing**: Fork, create feature branch, submit PR
- **License**: Educational/demonstration purposes (POC)

---

**🎉 Ready to start?** Check out the **[Complete Setup Guide](./GETTING_STARTED.md)** for detailed installation instructions!
