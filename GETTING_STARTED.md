# 🚀 Employee Face Recognition System - Getting Started Guide

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-brightgreen.svg)](https://vuejs.org/)
[![Ionic](https://img.shields.io/badge/Ionic-8.0-blue.svg)](https://ionicframework.com/)
[![Angular](https://img.shields.io/badge/Angular-20.0-red.svg)](https://angular.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📌 Quick Overview

This is a complete **Employee Time Tracking System using Facial Recognition** built with modern technologies. The system consists of three main components:

- **🖥️ Admin Panel** - Vue.js 3 web dashboard for administration
- **⚙️ Backend** - FastAPI core with face recognition capabilities  
- **📱 Employee Register** - Ionic/Angular mobile app for tablets/smartphones

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │     Backend     │    │ Employee App    │
│    (Vue.js 3)   │◄──►│   (FastAPI)     │◄──►│  (Ionic/Angular)│
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Face Recognition │ │ • Photo Capture │
│ • User Mgmt     │    │ • JWT Auth      │    │ • Check-in/out  │
│ • Reports       │    │ • MySQL DB      │    │ • Real-time     │
│ • Analytics     │    │ • API Endpoints │    │ • Offline Mode  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

### Required Software
- **Node.js** 18+ ([Download](https://nodejs.org))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **VS Code** ([Download](https://code.visualstudio.com/)) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### For Mobile Development (Optional)
- **Android Studio** ([Download](https://developer.android.com/studio))
- **Ionic CLI**: `npm install -g @ionic/cli`

### System Requirements
- **Windows 10/11**, **macOS**, or **Linux Ubuntu 20.04+**
- **8GB RAM** minimum (16GB recommended)
- **5GB free disk space**

## 🚀 Quick Start (Recommended Path)

### Option 1: VS Code Dev Container (Easiest - Backend Only)

> ⚠️ **Note**: Dev Container setup is currently optimized for backend development only due to complex native dependencies (dlib, face_recognition).

1. **Clone the repository**
   ```bash
   git clone https://github.com/xxxxxxxxxxxxxxxxxxx.git
   cd project
   ```

2. **Open in VS Code**
   ```bash
   code .
   ```

3. **Reopen in Container**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Select: **"Dev Containers: Reopen in Container"**
   - Wait for container to build (first time takes 5-10 minutes)

4. **Inside the container**, start the backend:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload
   ```

5. **Set up admin panel** (in a new terminal):
   ```bash
   cd admin-panel
   npm install
   npm run dev
   ```

✅ **Access Points:**
- **Backend API**: http://localhost:8081/docs
- **Admin Panel**: http://localhost:3000

### Option 2: Manual Setup (All Components)

If you prefer manual setup or want to develop all components:

#### 🔧 Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Activate (Linux/macOS)
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your settings
   # DB_USER=root
   # DB_PASSWORD=your_password
   # JWT_SECRET_KEY=your-secret-key
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload
   ```

#### 🖥️ Admin Panel Setup

1. **Navigate to admin panel**
   ```bash
   cd admin-panel
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Development mode** (recommended)
   ```bash
   npm run dev
   # Access at http://localhost:3000
   ```

4. **Production build** (optional)
   ```bash
   npm run build:prod
   # Integrates with backend at http://localhost:8081/admin/
   ```

#### 📱 Employee Mobile App Setup

1. **Navigate to employee register**
   ```bash
   cd employee-register
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Web development**
   ```bash
   ionic serve
   # Access at http://localhost:8100
   ```

4. **Android development** (optional)
   ```bash
   ionic build
   npx cap sync android
   npx cap open android
   ```

## 🐳 Docker Quick Start

For production-like environment or easy deployment:

```bash
# Start all services with Docker
docker-compose up --build

# Access points:
# - Backend: http://localhost:8081
# - Admin Panel: http://localhost:8081/admin/
```

## 📁 Project Structure

```
employee-face-recognition-system/
├── 🖥️ admin-panel/              # Vue.js 3 Admin Dashboard
│   ├── src/
│   │   ├── components/         # Reusable Vue components
│   │   ├── views/             # Page components
│   │   ├── router/            # Vue Router configuration
│   │   └── store/             # Pinia state management
│   ├── scripts/               # Build and deployment scripts
│   ├── package.json
│   └── vite.config.js
│
├── ⚙️ backend/                  # FastAPI Core API
│   ├── controllers/           # API route handlers
│   ├── services/              # Business logic
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic schemas
│   ├── utils/                 # Utilities (JWT, etc.)
│   ├── tests/                 # Test suites
│   ├── alembic/               # Database migrations
│   ├── .devcontainer/         # VS Code dev container config
│   ├── requirements.txt
│   ├── Dockerfile
│   └── main.py
│
├── 📱 employee-register/        # Ionic/Angular Mobile App
│   ├── src/
│   │   ├── app/               # Angular application
│   │   └── environments/      # Environment configs
│   ├── android/               # Android native project
│   ├── capacitor.config.ts
│   └── package.json
│
└── 📚 Documentation & Scripts
    ├── README.md              # This file
    ├── steps.md               # Detailed setup steps
    └── docker-compose.yml     # Docker orchestration
```

## 🔑 Key Features

### Admin Panel (Vue.js)
- **Dashboard**: Real-time metrics and analytics
- **Employee Management**: Add, edit, view employees
- **Company Management**: Multi-tenant support
- **Access Logs**: View and export employee access history
- **User Management**: Admin user accounts and roles
- **Reports**: Generate PDF/CSV reports
- **Responsive Design**: Works on desktop and mobile

### Backend (FastAPI)
- **Face Recognition**: Using dlib and face_recognition library
- **JWT Authentication**: Secure API access
- **Multi-tenant**: Company-based data isolation
- **Database**: MySQL with SQLAlchemy ORM
- **API Documentation**: Automatic OpenAPI/Swagger docs
- **Testing**: Comprehensive test suite with pytest
- **Docker Ready**: Containerized for easy deployment

### Employee Mobile App (Ionic/Angular)
- **Photo Capture**: Native camera integration
- **Face Registration**: Register employee faces
- **Check-in/Check-out**: Automatic time tracking
- **Offline Support**: Works without internet connection
- **Cross-platform**: Android, iOS, and web
- **Real-time Sync**: Syncs with backend when online

## 🌐 Access Points

Once everything is running:

| Service | Development | Production |
|---------|-------------|------------|
| **Backend API** | http://localhost:8081 | Your server:8081 |
| **API Documentation** | http://localhost:8081/docs | Your server:8081/docs |
| **Admin Panel** | http://localhost:3000 | http://localhost:8081/admin/ |
| **Mobile App** | http://localhost:8100 | Native app |

## 🔧 Development Workflows

### For Backend Development
```bash
# Use VS Code Dev Container (recommended)
code .
# Select "Reopen in Container"

# Or manual setup
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### For Frontend Development
```bash
# Admin Panel
cd admin-panel
npm install
npm run dev

# Mobile App
cd employee-register
npm install
ionic serve
```

### For Full-Stack Development
```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Admin Panel  
cd admin-panel && npm run dev

# Terminal 3: Mobile App
cd employee-register && ionic serve
```

## 🔍 Testing

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest --cov=.           # Run with coverage
pytest tests/test_face_recognition.py  # Specific test
```

### Frontend Tests
```bash
# Admin Panel
cd admin-panel
npm run test

# Mobile App
cd employee-register
npm run test
```

## 🚨 Common Issues & Solutions

### Backend Issues

**Problem**: `dlib` installation fails on Windows
```bash
# Solution: Use dev container or install build tools
# Option 1: Use VS Code Dev Container (recommended)
# Option 2: Install Visual Studio Build Tools + CMake
pip install dlib-bin  # Alternative pre-built version
```

**Problem**: Database connection errors
```bash
# Check database credentials in .env
# Ensure MySQL is running
# Run migrations: alembic upgrade head
```

### Frontend Issues

**Problem**: CORS errors
```bash
# Admin panel connects via proxy (vite.config.js)
# Check backend CORS settings in main.py
```

**Problem**: Node.js version conflicts
```bash
# Use Node Version Manager (nvm)
nvm use 18  # Use Node.js 18
```

### Mobile App Issues

**Problem**: Camera not working on Android
```bash
# Check permissions in android/app/src/main/AndroidManifest.xml
# Enable camera permission in device settings
```

**Problem**: Network errors on Android emulator
```bash
# Use http://10.0.2.2:8081 for backend URL in emulator
# Or use your computer's IP address for physical device
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js 3 Guide](https://vuejs.org/guide/)
- [Ionic Framework Docs](https://ionicframework.com/docs)
- [face_recognition Library](https://github.com/ageitgey/face_recognition)

### Development Tools
- [VS Code Extensions Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-typescript-next)
- [Vue.js DevTools](https://devtools.vuejs.org/)
- [Postman Collection](http://localhost:8081/docs) (API testing)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📞 Support

For issues and questions:

1. **Check this guide** first
2. **Review error logs** in terminal/console
3. **Search existing issues** on GitHub
4. **Create a new issue** with:
   - Error message
   - Steps to reproduce
   - Your operating system
   - Node.js/Python versions

## 🔐 Security Notes

This is a **Proof of Concept (POC)**. For production deployment:

- [ ] Change all default passwords
- [ ] Use HTTPS in production
- [ ] Implement proper backup strategy
- [ ] Review security settings
- [ ] Add rate limiting
- [ ] Implement proper logging
- [ ] Comply with data privacy regulations (GDPR, CCPA)

## 📄 License

This project is developed as a Proof of Concept for educational and demonstration purposes.

---

**🎉 You're all set!** Start with the VS Code Dev Container for the easiest backend development experience, then expand to other components as needed.