# Route Map

This document outlines the API endpoints and their implementation status.

## Authentication
- [x] `POST /auth/register`: Register a new company.
- [x] `POST /auth/login`: Authenticate and receive a JWT token.

## Employees
- [x] `POST /employees/register_face`: Register a new face for an employee.
- [x] `POST /employees/check_in_out`: Perform a check-in or check-out for an employee using face recognition.
- [x] `GET /employees`: List all employees.

## Logs
- [x] `GET /logs/access`: Get access logs.
- [x] `GET /logs/login`: Get login logs.

## Health
- [x] `GET /health`: Health check endpoint.
