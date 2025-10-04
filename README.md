
# Employee Time Tracker - Face Recognition System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-20.0-red.svg)](https://angular.io/)
[![Ionic](https://img.shields.io/badge/Ionic-8.0-blue.svg)](https://ionicframework.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

## 📌 Overview

This project is a **Proof of Concept (POC)** for an employee time tracking system using **facial recognition technology**. The system allows employee registration, authentication, and automatic check-in/check-out logging through facial biometric verification.

The application consists of two main components working together:

* **Frontend**: Built with **Angular 20 + Ionic 8 + Capacitor 7**, it provides a mobile-first interface for capturing employee photos using the device camera.
* **Backend**: Developed in **Python with FastAPI**, it processes facial recognition, manages employee data, and logs access events in a MySQL database.

The backend is containerized with **Docker** for easy deployment in testing and production environments.

---

## 🏗️ Architecture

### Project Structure

```
face_recognition_test/
├── backend/                    # FastAPI backend application
│   ├── controllers/           # API route controllers
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── employees.py      # Employee management & face recognition
│   │   └── logs.py           # Access log endpoints
│   ├── services/             # Business logic layer
│   │   ├── auth_service.py   # Authentication service
│   │   ├── company_service.py # Company management
│   │   ├── face_recognition_service.py # Face processing
│   │   └── log_service.py    # Access log service
│   ├── models/               # SQLAlchemy database models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── utils/                # Utility functions (JWT, security)
│   ├── alembic/              # Database migrations
│   ├── tests/                # Unit and integration tests
│   ├── main.py               # FastAPI application entry point
│   ├── database.py           # Database configuration
│   ├── dependencies.py       # Dependency injection
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker configuration
│   └── docker-compose.yml    # Docker Compose setup
│
└── employee-register/         # Ionic/Angular frontend
    ├── android/              # Android native project
    ├── src/
    │   ├── app/             # Application components
    │   └── environments/    # Environment configurations
    ├── capacitor.config.ts  # Capacitor configuration
    └── package.json         # Node.js dependencies
```

### Technology Stack

#### Backend

* **Framework**: FastAPI (Python 3.11+)
* **Database**: MySQL with SQLAlchemy ORM
* **Face Recognition**: face_recognition library (dlib-based)
* **Authentication**: JWT tokens with bcrypt password hashing
* **Image Processing**: OpenCV, Pillow, NumPy
* **Migrations**: Alembic
* **Containerization**: Docker & Docker Compose
* **Testing**: Pytest

#### Frontend

* **Framework**: Angular 20 (Standalone Components)
* **Mobile Framework**: Ionic 8
* **Native Bridge**: Capacitor 7
* **Language**: TypeScript 5.8
* **Camera Integration**: @capacitor/camera
* **HTTP Client**: Angular HttpClient with RxJS
* **Platform**: Web + Android (iOS ready)

---

## 🚀 Installation & Setup

### Prerequisites

* **Node.js** 18+ and npm
* **Python** 3.11+
* **MySQL** 8.0+
* **Docker** & Docker Compose (optional, for containerized deployment)
* **Android Studio** (for Android development)
* **CMake** and **C++ Build Tools** (for building dlib on Windows)

### Backend Setup

#### Option 1: Local Development

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with:
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=employee_tracker
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

API Documentation will be available at: **http://localhost:8081/docs**

#### Option 2: Docker Deployment

```bash
cd backend

# Build and start containers
docker-compose up --build

# The API will be available at http://localhost:8081
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd employee-register

# Install dependencies
npm install

# Run in browser (development)
ionic serve

# Build for production
npm run build

# For Android deployment
ionic build
npx cap sync android
npx cap open android

# Run on Android device/emulator
npx cap run android
```

#### Android Configuration

The project includes necessary Android permissions and network security configuration:

* **Camera Permission**: Configured in `AndroidManifest.xml`
* **Cleartext Traffic**: Enabled for local development
* **Network Security Config**: Allows HTTP connections to localhost/LAN during development

For emulator testing, the backend should be accessed via `http://10.0.2.2:8081`

---

## 🔐 Authentication & Security

The system implements JWT-based authentication:

1. **Company Registration**: Companies register with credentials
2. **Login**: Obtain JWT access token
3. **Protected Endpoints**: Employee and log endpoints require valid JWT
4. **Password Security**: Bcrypt hashing with salt
5. **Token Expiration**: Configurable token lifetime

### Authentication Flow

```
1. POST /auth/register → Register company
2. POST /auth/login → Get JWT token
3. Use token in Authorization header: "Bearer <token>"
4. Access protected endpoints
```

---

## 🎯 Core Features

### 1. Employee Enrollment

* Capture employee photo via camera
* Extract facial features using dlib's face recognition
* Store 128-dimensional face encoding in database
* Support multiple face encodings per employee
* Real-time face detection validation

### 2. Facial Recognition Check-in/Check-out

* Capture photo for verification
* Compare against all registered employees
* Calculate Euclidean distance between face encodings
* Match with configurable tolerance threshold (default: 0.6)
* Automatic event type determination (in/out based on last log)
* Store access logs with timestamp

### 3. Access Log Management

* View employee access history
* Filter logs by employee, date range, or event type
* Export log data
* Real-time access tracking

### 4. Multi-tenant Support

* Company-based authentication
* Isolated data per company
* Scalable architecture

---

## 🔄 Application Workflow

### Employee Registration Flow

```
1. Open mobile app
2. Navigate to registration
3. Enter employee details (name, etc.)
4. Capture photo using device camera
5. App sends image (base64) to backend
6. Backend detects face and extracts encoding
7. Encoding stored in database
8. Success confirmation returned to app
```

### Check-in/Check-out Flow

```
1. Employee opens app
2. Tap "Check In/Out" button
3. Camera captures employee photo
4. Photo sent to backend for verification
5. Backend compares with all stored face encodings
6. If match found (distance < tolerance):
   - Determine event type (in/out) based on last log
   - Create access log entry
   - Return employee info and event type
7. Display result to employee
```

---

## 📡 API Endpoints

### Authentication

* `POST /auth/register` - Register new company
* `POST /auth/login` - Login and obtain JWT token

### Employee Management

* `POST /employees/register_face` - Register employee with facial data
* `POST /employees/check_in_out` - Verify employee and log access
* `GET /employees` - List all employees (protected)

### Access Logs

* `GET /logs` - Retrieve access logs (protected)
* `GET /logs/{employee_id}` - Get logs for specific employee (protected)

### Health Check

* `GET /health` - API health status

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_face_recognition.py
```

### Test Coverage

* Face recognition service tests
* Authentication flow tests
* API endpoint tests
* Database model tests

---

## 🐳 Docker Deployment

### Development Environment

```bash
cd backend
docker-compose up
```

### Production Deployment

```bash
# Build production image
docker build -t employee-tracker-api:latest .

# Run with production settings
docker run -d \
  -p 8081:8081 \
  -e DB_HOST=your-db-host \
  -e DB_USER=your-db-user \
  -e DB_PASSWORD=your-db-password \
  -e DB_DATABASE=employee_tracker \
  -e JWT_SECRET=your-production-secret \
  --name employee-tracker-api \
  employee-tracker-api:latest
```

### Using Docker Compose

The included `docker-compose.yml` sets up:
* FastAPI backend service
* MySQL database
* Volume persistence for database data
* Network isolation
* Health checks

---

## ⚙️ Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 3306 |
| `DB_USER` | Database user | root |
| `DB_PASSWORD` | Database password | - |
| `DB_DATABASE` | Database name | employee_tracker |
| `JWT_SECRET` | Secret key for JWT | - |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_EXPIRE_MINUTES` | Token expiration | 30 |

### Frontend Environment

Configure API endpoint in `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8081'
};
```

For Android emulator: Use `http://10.0.2.2:8081`  
For physical device: Use your computer's LAN IP (e.g., `http://192.168.1.100:8081`)

---

## 🔧 Face Recognition Configuration

### Tolerance Threshold

The system uses Euclidean distance to compare face encodings. Adjust the `TOLERANCE` value in `backend/controllers/employees.py`:

* **0.5** - Stricter matching (fewer false positives, may reject valid faces)
* **0.6** - Balanced (default, recommended)
* **0.7** - Looser matching (more false positives, accepts more variations)

### Face Detection Model

Currently uses HOG (Histogram of Oriented Gradients) for CPU-friendly processing:
* Fast processing on CPU
* Good accuracy for frontal faces
* Suitable for POC and development

For production with GPU:
* Change model to "cnn" in `face_recognition_service.py`
* Better accuracy with varied angles
* Requires CUDA-enabled GPU

---

## 📋 Database Schema

### Main Tables

* **companies** - Company/organization information
* **employees** - Employee basic information
* **face_encodings** - Facial feature vectors (128-dim)
* **access_logs** - Check-in/check-out events

### Relationships

* Company → Employees (one-to-many)
* Employee → Face Encodings (one-to-many)
* Employee → Access Logs (one-to-many)

---

## 🚨 Known Limitations (POC)

* **Single Face Detection**: Only processes the first detected face per image
* **Lighting Sensitivity**: Performance degrades in poor lighting conditions
* **Frontal Face**: Best results with frontal face photos
* **CPU Processing**: HOG model used for CPU compatibility (slower than CNN)
* **No Live Detection**: Cannot detect photo spoofing attacks
* **Basic Security**: Demo authentication, not production-hardened

---

## 🛣️ Roadmap

### Planned Features

- [ ] Multiple employee face registration per person
- [ ] Live face detection (anti-spoofing)
- [ ] Face mask detection support
- [ ] GPS location tracking for check-ins
- [ ] Push notifications for access events
- [ ] Web dashboard for administrators
- [ ] iOS application support
- [ ] Advanced reporting and analytics
- [ ] Integration with HR systems
- [ ] Offline mode support
- [ ] Biometric encryption for face data

---

## 🤝 Contributing

This is a POC project for demonstration purposes. Feel free to fork and adapt for your needs.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is developed as a **Proof of Concept (POC)** for educational and demonstration purposes. It is not intended for production use without proper security audits and enhancements.

---

## 👥 Authors

* **senseiRoa** - Initial work - [GitHub Profile](https://github.com/senseiRoa)

---

## 🙏 Acknowledgments

* **face_recognition** library by Adam Geitgey
* **dlib** machine learning library
* **FastAPI** framework
* **Ionic Framework** and **Angular** teams
* **Capacitor** for native mobile integration

---

## 📞 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

## 🔗 Useful Links

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [Ionic Documentation](https://ionicframework.com/docs)
* [face_recognition Library](https://github.com/ageitgey/face_recognition)
* [Capacitor Documentation](https://capacitorjs.com/docs)
* [Angular Documentation](https://angular.io/docs)

---

**Note**: This is a POC implementation. Before deploying to production, ensure proper security measures, scalability considerations, and compliance with data privacy regulations (GDPR, CCPA, etc.) are implemented.

