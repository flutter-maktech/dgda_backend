# 🛡️ DGDA Backend API (FastAPI)

Production-grade asynchronous REST API for the **DGDA Mobile Application** and **English Admin Portal**.

---

## 🚀 Key Features

* **Framework**: FastAPI (Python 3.10+) with full Asynchronous I/O.
* **Authentication**: State-of-the-art JWT (JSON Web Tokens) with dual token architecture:
  * **Short-lived Access Token** (60 minutes) for authorized requests.
  * **Long-lived Refresh Token** (7 days) for seamless token renewals.
  * **Password Security**: Bcrypt hashing with salted rounds.
* **Role-Based Access Control (RBAC)**: Supports `ADMIN`, `STAFF`, and `USER` roles.
* **Database & High Concurrency**:
  * Asynchronous SQLAlchemy 2.0 with connection pooling (`pool_size=20`, `max_overflow=10`).
  * Default: High-speed async SQLite (`sqlite+aiosqlite:///./dgda.db`) for immediate zero-config development.
  * Production ready: 1-line switch to PostgreSQL (`postgresql+asyncpg://...`).
* **Traffic Control & DDoS Protection**:
  * Built-in Rate Limiting via `slowapi` on sensitive endpoints (`/auth/login`, `/auth/register`).
* **CORS Configured**: Ready for Flutter Mobile app and Web Admin Panel.
* **Interactive API Docs**: Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                  # Auth & DB dependencies (get_current_user, get_db)
│   │   └── v1/
│   │       ├── api.py               # Router aggregator
│   │       └── endpoints/
│   │           └── auth.py          # /register, /login, /refresh, /me, /change-password
│   ├── core/
│   │   ├── config.py                # Pydantic Settings & .env loading
│   │   ├── database.py              # Async SQLAlchemy engine & connection pool
│   │   ├── limiter.py               # Rate limiting engine
│   │   └── security.py              # Bcrypt & JWT token creation/decoding
│   ├── crud/
│   │   └── crud_user.py             # User DB operations
│   ├── models/
│   │   └── user.py                  # SQLAlchemy User model & roles
│   ├── schemas/
│   │   └── user.py                  # Pydantic validation schemas
│   └── main.py                      # FastAPI app entrypoint, CORS & Lifespan
├── .env                             # Active environment configuration
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
└── run.py                           # Convenient server launcher
```

---

## ⚡ How to Run

### 1. Activate Virtual Environment:
```powershell
# Windows PowerShell
.\backend\venv\Scripts\Activate.ps1
```

### 2. Run the Server:
```powershell
python .\backend\run.py
```
Or with Uvicorn:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
* **Base URL**: `http://localhost:8000`
* **Swagger UI Documentation**: `http://localhost:8000/docs`
* **ReDoc Documentation**: `http://localhost:8000/redoc`

---

## 🔑 Default Seeded Admin Credentials

On first run, the database is automatically created and seeded with a default administrator:

* **Email**: `admin@dgda.gouv.cd`
* **Password**: `Admin@DGDA2026!`
* **Role**: `ADMIN`

---

## 📋 Authentication Endpoints Overview

| Method | Endpoint | Description | Protected |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user | No (Rate Limited) |
| `POST` | `/api/v1/auth/login` | Login with email & password | No (Rate Limited) |
| `POST` | `/api/v1/auth/refresh` | Renew access token with refresh token | No |
| `GET` | `/api/v1/auth/me` | Fetch logged-in user profile | **Yes (Bearer Token)** |
| `PUT` | `/api/v1/auth/me` | Update logged-in user profile | **Yes (Bearer Token)** |
| `POST` | `/api/v1/auth/change-password` | Change user password | **Yes (Bearer Token)** |
| `GET` | `/health` | Check API health | No |
