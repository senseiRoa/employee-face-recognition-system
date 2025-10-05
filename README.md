
# 🚀 Employee Face Recognition System

[![FastAPI](https://img.shie## 📋 Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **VS Code** + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## 🎯 Key Features

### 🖥️ Admin Panel (Vue.js 3)
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
│   ├── .devcontainer/         # VS Code dev container config
│   ├── tests/                 # Test suites
│   └── main.py
│
└── 📱 employee-register/        # Ionic/Angular Mobile App
    ├── src/app/               # Angular application
    ├── android/               # Android native project
    └── capacitor.config.ts
```

## 🚨 Important Notes

> **⚠️ Dev Container Support**: Only the backend currently supports VS Code Dev Container due to complex native dependencies (dlib, face_recognition library).

> **🔐 Security**: This is a Proof of Concept. For production use, implement proper security measures, HTTPS, and comply with data privacy regulations.

## 📚 Documentation

- **[📋 Complete Setup Guide](./GETTING_STARTED.md)** - Detailed installation and configuration
- **[🐳 Docker Guide](./.devcontainer/)** - Dev container and Docker setup
- **[🧪 Testing Guide](./backend/tests/)** - Running and writing tests
- **[📊 API Documentation](http://localhost:8081/docs)** - OpenAPI/Swagger docs (when running)

## 📞 Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/senseiRoa/employee-face-recognition-system/issues)
- **Contributing**: Fork, create feature branch, submit PR
- **License**: Educational/demonstration purposes (POC)

---

**🎉 Ready to start?** Check out the **[GETTING_STARTED.md](./GETTING_STARTED.md)** guide for complete setup instructions!/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-brightgreen.svg)](https://vuejs.org/)
[![Ionic](https://img.shields.io/badge/Ionic-8.0-blue.svg)](https://ionicframework.com/)
[![Angular](https://img.shields.io/badge/Angular-20.0-red.svg)](https://angular.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📌 Overview

This is a complete **Employee Time Tracking System using Facial Recognition** built with modern technologies. The system provides a comprehensive solution for employee management, time tracking, and administration through facial biometric verification.

## 🚀 **[👉 GET STARTED HERE - Complete Setup Guide](./GETTING_STARTED.md)**

## 🏗️ System Components

The application consists of three main components:

* **🖥️ Admin Panel** - Vue.js 3 web dashboard for comprehensive administration and analytics
* **⚙️ Backend** - FastAPI core with face recognition, JWT authentication, and MySQL database  
* **📱 Employee Register** - Ionic/Angular mobile app for tablets and smartphones

> **Note**: Only the backend currently supports Dev Container setup due to complex native dependencies (dlib, face_recognition).

## � Quick Access

| Component | Purpose | Technology | Access |
|-----------|---------|------------|---------|
| **Admin Panel** | Management dashboard | Vue.js 3 | http://localhost:3031 |
| **Backend API** | Core services & Face Recognition | FastAPI + Python | http://localhost:8081/docs |
| **Employee App** | Mobile check-in/out | Ionic + Angular | http://localhost:8100 |

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

### � Option 3: Docker (Production-like)
```bash
docker-compose up --build
# Access: http://localhost:8081
```

## � Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **VS Code** + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

