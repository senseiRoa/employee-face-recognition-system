# Work Plan

This document outlines the steps taken to refactor the Employee Face Recognition POC.

### 1. Backend Refactoring (`backend/main.py`)

* **Objective**: Modify the backend to automatically generate a unique ID for each new employee.
* **Actions**:
  * Imported the `uuid` module.
  * Modified the `Employee` SQLAlchemy model to use a `UUID` as the primary key with a default value factory.
  * Updated the `RegisterFaceReq` Pydantic schema to remove the `employee_id` field.
  * Modified the `/register_face` endpoint to generate a new UUID for each employee, save it to the database, and return the new ID in the response.

### 2. Frontend Service Update (`employee-register/src/app/services/api.service.ts`)

* **Objective**: Align the frontend API service with the backend changes.
* **Actions**:
  * Updated the `registerFace` method signature to remove the `employee_id` parameter.
  * Adjusted the `post` request to send only the `name` and `image_base64`.

### 3. Create New Frontend Components

* **Objective**: Create new, separate pages for the registration and check-in/out functionalities.
* **Actions**:
  * Used the Angular CLI (`ng`) to generate new `register` and `check` standalone components inside `src/app/pages`.
  * Resolved environment issues related to `npm install` and the correct command for generating components.

### 4. Implement the Register Page (`employee-register/src/app/pages/register/`)

* **Objective**: Implement the user interface and logic for the new employee registration page.
* **Actions**:
  * Created the HTML template (`register.component.html`) with an input for the employee's `name` and a button to trigger registration. The old `employee_id` input was removed.
  * Implemented the component logic (`register.component.ts`) to capture the name and photo, call the updated `api.service.ts#registerFace`, and display the new `employee_id` returned by the backend.

### 5. Implement the Check-in/out Page (`employee-register/src/app/pages/check/`)

* **Objective**: Move the check-in/out functionality to its own dedicated page.
* **Actions**:
  * Moved the check-in/out logic from `home.page.ts` to `check.component.ts`.
  * Moved the corresponding HTML from `home.page.html` to `check.component.html`.

### 6. Update App Navigation and Routing

* **Objective**: Update the main page to be a menu and configure the routing for the new pages.
* **Actions**:
  * Modified `home.page.html` to act as a menu with navigation buttons to the `/register` and `/check` pages.
  * Removed the old, unused logic from `home.page.ts`.
  * Updated `employee-register/src/app/app.routes.ts` to include the routes for the new `/register` and `/check` pages.
