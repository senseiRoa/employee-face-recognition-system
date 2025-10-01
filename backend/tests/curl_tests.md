# cURL Scripts for API Testing

This document provides cURL commands to test the main endpoints of the refactored Face Recognition API.

**Note:** Before running these commands, you need to replace the placeholder values:
- `YOUR_JWT_TOKEN`: Replace with a valid JWT token obtained from your authentication provider.
- `YOUR_BASE64_IMAGE_STRING`: Replace with a valid base64 encoded string of a face image.

---

## 1. Register a New Employee

This command registers a new employee with their ID, name, and face image.

```bash
curl -X POST "http://localhost:8001/employees" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d 
'{
  "employee_id": "emp-001",
  "name": "John Doe",
  "image_base64": "YOUR_BASE64_IMAGE_STRING"
}'
```

---

## 2. List All Employees

This command retrieves a list of all registered employees.

```bash
curl -X GET "http://localhost:8001/employees" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 3. Recognize a Face (Check-in/Check-out)

This command sends an image to the recognition endpoint to identify an employee.

```bash
curl -X POST "http://localhost:8001/check_in_out" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-d 
'{
  "image_base64": "YOUR_BASE64_IMAGE_STRING"
}'
```
