# Refactored Face Recognition API

This document provides instructions for setting up and running the refactored face recognition backend. The project is built with FastAPI, follows a Hexagonal Architecture, and runs in a Docker environment.

---

## 1. Environment Setup

This project is designed to be run with Docker and Docker Compose.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Configuration

The application is configured using environment variables, which are passed to the containers via the `docker-compose.yml` file.

Key environment variables for the `api` service:
- `DATABASE_URL`: The connection string for the MySQL database.
- `INTROSPECTION_URL`: The URL of the JWT introspection endpoint for token validation.
- `INTROSPECTION_AUTH_HEADER`: The `Authorization` header value required to communicate with the introspection endpoint.

### Running the Application

1.  **Navigate to the `backend` directory.**

2.  **Build and start the services:**

    ```bash
    docker-compose up --build
    ```

    This command will:
    - Build the `api` image based on the `Dockerfile`.
    - Start the `api` service (FastAPI application).
    - Start the `db` service (MySQL 8 database).

    The API will be available at `http://localhost:8001`.

3.  **Running Database Migrations:**

    After starting the services, you may need to run the database migrations to create the necessary tables.

    Open a new terminal and execute the following command:

    ```bash
    docker-compose exec api alembic upgrade head
    ```

---

## 2. Running Tests

The primary method for testing the API is by using the provided cURL scripts.

### cURL Tests

A collection of cURL commands for testing the main endpoints is available in `tests/curl_tests.md`.

**Note:** Before running these commands, you need to replace the placeholder values (`YOUR_JWT_TOKEN`, `YOUR_BASE64_IMAGE_STRING`) as described in the file.

---

## 3. Available Endpoints

All endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

### Authentication

- **POST `/token`**: (Not implemented in this project) This is the `tokenUrl` for the OAuth2 flow. You should obtain a token from your authentication provider.

### Employees

- **POST `/employees`**: Register a new employee.
  - **Body**:
    ```json
    {
      "employee_id": "string",
      "name": "string",
      "image_base64": "string"
    }
    ```

- **GET `/employees`**: Get a list of all registered employees.

### Recognition

- **POST `/check_in_out`**: Recognize a face from an image.
  - **Body**:
    ```json
    {
      "image_base64": "string"
    }
    ```
    - **Success Response (200 OK)**:
      ```json
      {
        "recognized": true,
        "employee_id": "string"
      }
      ```
    - **Failure Response (200 OK)**:
      ```json
      {
        "recognized": false
      }
      ```
