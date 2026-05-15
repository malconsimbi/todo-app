# Full-Stack To-Do Application

A modern full-stack To-Do application built with:

* **Backend:** FastAPI + JWT Authentication
* **Frontend:** React 18 + TypeScript
* **Authentication:** JWT Bearer Tokens
* **Security:** bcrypt password hashing
* **Features:** Full CRUD operations, protected routes, validation, request logging, and persistent authentication

---

# Tech Stack

## Backend

* Python 3.8+
* FastAPI
* Uvicorn
* Pydantic
* Passlib (bcrypt)
* Python-JOSE (JWT)

## Frontend

* React 18
* TypeScript
* React Router DOM
* Axios

---

# Project Structure

```text
todo-app/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── venv/
│
└── frontend/
    ├── public/
    │   └── index.html
    │
    ├── src/
    │   ├── api/
    │   │   └── client.ts
    │   │
    │   ├── components/
    │   │   ├── PrivateRoute.tsx
    │   │   └── Spinner.tsx
    │   │
    │   ├── hooks/
    │   │   └── useAuth.tsx
    │   │
    │   ├── pages/
    │   │   ├── LoginPage.tsx
    │   │   ├── RegisterPage.tsx
    │   │   └── TodosPage.tsx
    │   │
    │   ├── types/
    │   │   └── index.ts
    │   │
    │   ├── App.tsx
    │   ├── index.tsx
    │   └── index.css
    │
    ├── package.json
    └── tsconfig.json
```

---

# Features

* User registration
* User login with JWT authentication
* Protected routes
* Create todos
* Update todos
* Delete todos
* Mark todos as completed
* Persistent authentication
* Request validation
* Error handling
* API request logging

---

# Prerequisites

Install the following before running the project:

| Tool    | Version |
| ------- | ------- |
| Python  | 3.8+    |
| Node.js | 18+     |
| npm     | 9+      |

---

# Backend Setup (FastAPI)

## 1. Navigate to the backend folder

```bash
cd backend
```

---

## 2. Create a virtual environment

###(PowerShell)

```powershell
python -m venv venv
```


## 3. Activate the virtual environment

###(PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```
---

## 4. Install backend dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Run the FastAPI server

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

# Frontend Setup (React + TypeScript)

## 1. Open a new terminal

Keep the backend terminal running.

---

## 2. Navigate to the frontend folder

```bash
cd frontend
```

---

## 3. Install frontend dependencies

```bash
npm install
```
---

## 4. Start the React development server

```bash
npm start
```

Frontend runs at:

```text
http://localhost:3000
```

---

# Running the Full Application

## Terminal 1 — Backend

```bash
cd backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

---

## Terminal 2 — Frontend

```bash
cd frontend

npm install

npm start
```
