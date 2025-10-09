# Employee Time Tracker API

This is the backend API for the Employee Time Tracker application. It provides functionalities for face recognition-based employee clock-in/out, user management, and logging.

## 🚀 Quick Start

### Development Setup
- **[QUICK_START.md](./QUICK_START.md)** - Fast development setup
- **[VS Code Dev Container](./.devcontainer/)** - Containerized development

### Production Deployment
- **[DOCKER_BUILD_GUIDE.md](./DOCKER_BUILD_GUIDE.md)** - Complete Docker build process
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide

### Build & Deploy Commands
```bash
# Build complete system (admin-panel + backend)
./scripts/build-docker.sh -t v1.0.0 -p

# Quick local build
./scripts/build-docker.sh -l

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## Project Structure

The project is organized into the following structure:

```
backend/
├── alembic/           # Alembic migrations
├── controllers/       # API endpoints (routers)
├── models/            # SQLAlchemy database models (entities)
├── schemas/           # Pydantic data validation schemas
├── services/          # Business logic
├── utils/             # Utility functions (security, JWT)
├── database.py        # Database connection and session management
├── dependencies.py    # FastAPI dependencies (e.g., get_current_user)
├── main.py            # Main FastAPI application
├── requirements.txt   # Project dependencies
└── ...
```

### Modules

*   **`main.py`**: The main entry point of the application. It initializes the FastAPI app, includes the routers, and configures middleware.

*   **`database.py`**: Contains the SQLAlchemy engine, session factory, and a dependency to get a database session.

*   **`dependencies.py`**: Implements dependencies used across the application, such as `get_current_user` which validates the JWT token and retrieves the current user.

*   **`models/`**: Defines the SQLAlchemy models (database entities) that map to the database tables:
    *   `Employee`: Stores employee information.
    *   `FaceEncoding`: Stores face encodings for each employee.
    *   `AccessLog`: Logs employee clock-in/out events.
    *   `Company`: Stores company information for authentication.
    *   `LoginLog`: Logs company login events.

*   **`schemas/`**: Contains the Pydantic models used for data validation and serialization in the API endpoints.

*   **`controllers/`**: Each file in this directory corresponds to a specific domain and defines the API endpoints using FastAPI's `APIRouter`.
    *   `auth.py`: Handles company registration and login.
    *   `employees.py`: Manages employee and face recognition endpoints.
    *   `logs.py`: Provides access to access and login logs.

*   **`services/`**: This directory contains the core business logic of the application.
    *   `auth_service.py`: Implements the logic for user authentication.
    *   `company_service.py`: Manages the creation and retrieval of company data.
    *   `face_recognition_service.py`: Contains the logic for face encoding computation and comparison.
    *   `log_service.py`: Handles the retrieval of logs.

*   **`utils/`**: This directory holds utility functions.
    *   `jwt_handler.py`: **(Placeholder)** This module is responsible for JWT creation and validation. **WARNING**: The current implementation is a placeholder and not secure. It should be replaced with a proper JWT library like `python-jose` or `PyJWT` for production use.
    *   `security.py`: Provides password hashing and verification functions.

## API Endpoints

All endpoints (except for `/health`, `/auth/login`, and `/auth/register`) require a valid JWT token for authentication.

*   **Auth (`/auth`)**
    *   `POST /register`: Register a new company.
    *   `POST /login`: Authenticate and receive a JWT token.

*   **Employees (`/employees`)**
    *   `POST /register_face`: Register a new face for an employee.
    *   `POST /clock_in_out`: Perform a clock-in or clock-out for an employee using face recognition.
    *   `GET /employees`: List all employees.

*   **Logs (`/logs`)**
    *   `GET /access`: Get access logs.
    *   `GET /login`: Get login logs.

*   **Health (`/health`)**
    *   `GET /`: Health check endpoint.



## Getting Started
1. **Review project documentation:**

    * Read the files inside the `documentation/` folder to understand the architecture, dependencies, and usage guidelines before getting started.

2. **Run the project inside a DevContainer:**

    * Open the project in **VS Code**.
    * Make sure you have the **Dev Containers** extension installed.
    * Select **“Reopen in Container”** to launch the isolated environment (this helps avoid compatibility issues, especially with dependencies like `dlib`).

3. **Set up the database:**

    * Ensure the `.env` file contains the correct connection variables (`DATABASE_URL`).
    * Run Alembic migrations:

      ```bash
      alembic upgrade head
      ```

4. **Start the application:**
    Inside the container, run:

    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8081
    ```

    Once the environment is up, the application will be accessible at:
    [http://localhost:8081/health](http://localhost:8081/health)

---