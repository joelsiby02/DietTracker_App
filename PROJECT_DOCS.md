# Diet Tracker - In-Depth Technical Documentation

This document provides a detailed technical overview of the Diet Tracker application. It is intended for developers looking to understand the current architecture and to guide the future extension of the project into a dynamic web application with a separate frontend and backend.

## 1. Current Architecture (Streamlit Monolith)

The application is currently built as a **monolithic web application** using the Streamlit framework. In this model, the frontend (UI) and backend (business logic) are tightly coupled within the same Python script execution environment.

### Core Components

*   **`app.py` (Frontend & Controller):** This is the main entry point of the application. It is responsible for rendering the entire user interface using Streamlit widgets. It also acts as a controller, capturing user input (button clicks, form submissions) and calling the appropriate functions in the backend to process those actions. It heavily relies on `st.session_state` to maintain user state across interactions.

*   **`backend.py` (Business Logic / Service Layer):** This file contains the core business logic of the application. It is completely decoupled from the Streamlit UI. Its responsibilities include user authentication, database CRUD (Create, Read, Update, Delete) operations, and data calculations (e.g., calculating calories). Each function in this file is self-contained and manages its own database session, ensuring that connections are opened and closed properly for each operation.

*   **`database.py` (Data Access Layer & Models):** This file defines the structure of the database using SQLAlchemy ORM (Object-Relational Mapping). It contains the data models (`User`, `Food`, `Meal`, etc.) that map Python classes to database tables. It also includes the `get_session()` utility function, which provides a standard way to create a database session for any operation.

### Request/Response Flow

In Streamlit, the application flow is based on script re-runs:
1.  A user interacts with a widget in the browser (e.g., clicks a button).
2.  Streamlit sends this interaction information back to the Python server.
3.  The entire `app.py` script is re-executed from top to bottom.
4.  `st.session_state` is used to persist data (like the logged-in user or a partially built meal) between these re-runs.
5.  During the re-run, `app.py` calls functions in `backend.py` based on the user's action.
6.  The backend function executes its logic (e.g., queries the database) and returns a result.
7.  `app.py` uses this result to update the UI, which is then sent back to the browser.

---

## 2. Key Workflow Explanations

Understanding these key workflows is essential for refactoring the application.

### a. User Authentication

1.  **UI (`app.py`):** The login form collects a `username` and `password`.
2.  **Controller (`app.py`):** On form submission, it calls `self.backend.authenticate_user(username, password)`.
3.  **Backend (`backend.py`):** The `authenticate_user` function queries the `users` table for the given username. If found, it uses `bcrypt.checkpw` to compare the provided password with the stored hash.
4.  **Response:** The backend returns `(True, user_object)` on success or `(False, error_message)` on failure.
5.  **State (`app.py`):** On success, the `user_object` is stored in `st.session_state.user`, effectively logging the user in for the session.

### b. Meal Logging (Shopping Cart Model)

1.  **UI (`app.py`):** The "Log Meal" page displays a categorized browser of foods. Each food item has a quantity input and an "Add" button.
2.  **State (`app.py`):** When a user clicks "Add", the selected food object and its quantity are appended to a list in `st.session_state.meal_builder_items`. The script then re-runs.
3.  **Review (`app.py`):** The "Review and Log" section iterates through `st.session_state.meal_builder_items` to display the current "shopping cart" and calculate total macros for the meal.
4.  **Finalization (`app.py`):** When the user clicks "Log This Meal", the application creates a simplified list of `(food_id, quantity)` tuples from the session state.
5.  **Backend (`backend.py`):** This list is passed to `self.backend.log_meal()`. The backend function creates a new `Meal` record and then iterates through the list to create multiple `MealItem` records, all within a single database transaction.

### c. Destructive CSV Import (`import_foods_from_csv`)

This is a critical, destructive operation designed to completely replace a user's food and meal history.

1.  **UI (`app.py`):** The user uploads a CSV file on the "Import Foods" page.
2.  **Backend (`backend.py`):** The `import_foods_from_csv` function is called.
3.  **Data Deletion:** To prevent data integrity issues (i.e., "orphaned" meal items pointing to deleted foods), the function performs deletions in a specific order:
    *   It first finds all `Meal` IDs belonging to the user.
    *   It deletes all `MealItem` records associated with those `Meal` IDs.
    *   It then deletes all `Meal` records for the user.
    *   Finally, it deletes all `Food` records for the user.
4.  **Data Insertion:** The function then parses the uploaded CSV and creates new `Food` records for each row.
5.  **State (`app.py`):** The backend returns the names of the newly imported foods. These names are stored in `st.session_state.recently_imported_foods` to provide a filtered view on the "Log Meal" page.

---

## 3. Suggested Approach for React + Dynamic API Extension

The goal is to decouple the frontend from the backend. This involves transforming the `backend.py` logic into a standalone REST API and building a new React frontend to consume it. **FastAPI** is highly recommended for creating the API due to its performance, automatic documentation, and data validation features.

### Step 1: Create a REST API with FastAPI

The logic in `backend.py` can be refactored into API endpoints. A new file, `main.py` (or similar), would house the FastAPI application.

**Example Refactoring:**

*   **Current `backend.py` function:**
    ```python
    def get_user_foods(self, user_id):
        # ... database logic ...
        return foods
    ```

*   **New FastAPI endpoint in `main.py`:**
    ```python
    from fastapi import FastAPI, Depends
    # ... other imports

    app = FastAPI()

    # This function would handle getting the current user from a token
    async def get_current_user(...):
        # ... JWT token validation logic ...
        return user

    @app.get("/api/v1/foods")
    async def read_user_foods(current_user: User = Depends(get_current_user)):
        # The backend class can be instantiated here
        backend = MuscleTrackerBackend()
        foods = backend.get_user_foods(current_user.id)
        return foods
    ```

### Step 2: Implement Token-Based Authentication (JWT)

The current session-based login will not work with a decoupled frontend. It must be replaced with a token-based system.

1.  **Create a `/api/v1/token` endpoint.** This endpoint will accept a username and password.
2.  On successful authentication, it will generate a **JSON Web Token (JWT)** containing the `user_id` and an expiration time.
3.  This token is sent back to the React client.
4.  The React client must store this token (e.g., in `localStorage`) and include it in the `Authorization: Bearer <token>` header for all subsequent API requests that require authentication.
5.  FastAPI's `Depends` system can be used to create a dependency that validates this token on protected endpoints and provides the current user object.

### Step 3: Define API Endpoints

Map the existing backend functions to RESTful API endpoints.

| Method | Endpoint                       | Backend Function            | Description                                      |
| :----- | :----------------------------- | :-------------------------- | :----------------------------------------------- |
| `POST` | `/api/v1/token`                | `authenticate_user`         | Login and receive a JWT.                         |
| `POST` | `/api/v1/users`                | `create_user`               | Sign up a new user.                              |
| `GET`  | `/api/v1/dashboard/{date}`     | `get_daily_nutrition`       | Get nutrition summary for a specific date.       |
| `GET`  | `/api/v1/foods`                | `get_user_foods`            | Get a list of all foods for the logged-in user.  |
| `POST` | `/api/v1/foods`                | `add_food`                  | Add a single new food item.                      |
| `POST` | `/api/v1/foods/import`         | `import_foods_from_csv`     | Destructively import foods from a CSV.           |
| `POST` | `/api/v1/foods/upsert`         | `upsert_foods_from_csv`     | Non-destructively add/update from a CSV.         |
| `GET`  | `/api/v1/meals`                | `get_meal_logs`             | Get meal history, with date range filtering.     |
| `POST` | `/api/v1/meals`                | `log_meal`                  | Log a new meal with its items.                   |
| `GET`  | `/api/v1/sleep`                | `get_sleep_logs`            | Get sleep history.                               |
| `POST` | `/api/v1/sleep`                | `log_sleep`                 | Log or update a sleep entry for a specific date. |
| `GET`  | `/api/v1/export/health`        | `export_combined_logs`      | Export health data (Excel/JSON).                 |
| `GET`  | `/api/v1/export/foods`         | `get_user_foods`            | Export food database (CSV/JSON).                 |

### Step 4: Build the React Frontend

This will be a completely new project, likely bootstrapped with a tool like **Vite** or **Create React App**.

*   **UI Components:** Rebuild all the UI pages (Dashboard, Log Meal, etc.) as React components.
*   **API Service Layer:** Create a dedicated module (e.g., `api.js`) that uses `axios` or `fetch` to communicate with your new FastAPI backend. This layer will handle adding the JWT to headers.
*   **State Management:** Use a robust state management library like **Redux Toolkit** or **Zustand** to manage global state, such as the current user, authentication status, and food list. This replaces Streamlit's `st.session_state`.
*   **Routing:** Use **React Router** to handle client-side navigation between different pages.

### Project Structure (Future)

The project would evolve into a multi-directory monorepo or two separate repositories:

```
// Monorepo Structure Example

diet-tracker/
├── backend/                  # FastAPI Application
│   ├── main.py               # API endpoints
│   ├── business_logic.py     # Refactored from backend.py
│   ├── database.py           # (Unchanged)
│   └── ...
│
├── frontend/                 # React Application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page components (Dashboard, LogMeal)
│   │   ├── services/         # API communication layer
│   │   ├── store/            # Global state management (Redux/Zustand)
│   │   └── App.js
│   └── package.json
│
└── docker-compose.yml        # To run both services together
```

By following this roadmap, you can systematically and successfully migrate the Diet Tracker from a Streamlit monolith to a scalable, modern, and dynamic web application.
