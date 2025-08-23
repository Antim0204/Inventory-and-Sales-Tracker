# Inventory and Sales Tracker

A production-ready **Flask + PostgreSQL** backend application to manage **fuel inventory, pricing, and sales**, complete with reporting APIs, structured logging, tests, and Docker deployment.

---

## 📖 Overview

This project implements a backend system for a **Fuel Station Inventory & Sales Tracker**.  
It allows you to:

- Manage **Fuel Types** (CRUD, pricing history).
- Track **Inventory levels** (refill, deplete via sales).
- Record **Sales** transactions.
- Generate **Reports** (sales, revenue, stock, price history).
- Provide **Health/Meta endpoints** for monitoring.
- Run **unit & concurrency tests**.
- Deploy easily using **Docker + Gunicorn**.

---

## 🛠️ Tech Stack

- **Python 3.10**
- **Flask 3.x**
- **PostgreSQL 15**
- **SQLAlchemy 2.x**
- **Alembic** (DB migrations)
- **Flasgger** (Swagger UI)
- **pytest** (unit tests)
- **Docker + docker-compose**
- **python-dotenv** (env config)

---

## ⚙️ Setup Instructions

### 1. Clone & Install

```bash
git clone <repo-url>
cd Inventory-and-Sales-Tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)

Create `.env` in the project root:

```ini
FLASK_ENV=development
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fuel_db
DB_NAME_TEST=fuel_db_test
```

### 3. Run Locally

```bash
# initialize DB tables
psql "postgresql://postgres:postgres@localhost:5432/fuel_db" -f sql/001_init.sql

# start server
python main.py
```

Open Swagger docs at:  
👉 [http://localhost:5050/apidocs](http://localhost:5050/apidocs)

---

## 🗃️ Database & Migrations (Alembic)

Initialize Alembic:

```bash
alembic init migrations
```

Configure `migrations/env.py` to use your SQLAlchemy engine from `.env`.

Create new migration:

```bash
alembic revision -m "add sales indexes"
```

Apply migrations:

```bash
alembic upgrade head
```

---

## 🌐 API Endpoints

All endpoints return **JSON** and are available via Swagger UI.

### 🔹 Fuel Types
```http
POST /fuel-types
GET  /fuel-types
PUT  /fuel-types/{id}/price
```

Example (create):
```bash
curl -X POST http://localhost:5050/fuel-types   -H "Content-Type: application/json"   -d '{"name": "Diesel", "price_per_litre": "90.000", "initial_stock_litres":"100.000"}'
```

### 🔹 Inventory
```http
POST /inventory/refill
GET  /inventory
```

Example:
```bash
curl -X POST http://localhost:5050/inventory/refill   -H "Content-Type: application/json"   -d '{"fuel_type_id": 1, "litres": "200.000"}'
```

### 🔹 Sales
```http
POST /sales
GET  /sales
```

Example:
```bash
curl -X POST http://localhost:5050/sales   -H "Content-Type: application/json"   -d '{"fuel_type_id": 1, "litres": "50.000"}'
```

### 🔹 Reporting
```http
GET /reports/sales
GET /reports/revenue
GET /reports/inventory
GET /reports/price-history
```

Example:
```bash
curl "http://localhost:5050/reports/sales?from=2025-01-01&to=2025-12-31"
```

### 🔹 Meta / Health
```http
GET /health
```

---

## 📂 Project Structure

```
.
├── main.py                  # Entry point (creates and runs Flask app)
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── sql/
│   └── 001_init.sql         # Initial DB schema
├── src/
│   ├── __init__.py          # App factory, Swagger setup
│   ├── apis/                # API blueprints
│   │   ├── __init__.py
│   │   ├── fuel_types.py
│   │   ├── inventory.py
│   │   ├── sales.py
│   │   ├── reports.py
│   │   └── meta.py
│   ├── modules/             # Business logic (services)
│   │   ├── fuel_types_service.py
│   │   ├── inventory_service.py
│   │   ├── sales_service.py
│   │   └── reporting_service.py
│   ├── models/              # SQLAlchemy models
│   ├── utils/               # Helpers (decimal, logger, etc.)
│   ├── db.py                # DB session, engine, session_scope
│   └── errors.py            # Centralized error handling
└── tests/                   # pytest test suite
    ├── test_fuel_types.py
    ├── test_inventory.py
    ├── test_sales.py
    ├── test_reporting.py
    ├── test_validations.py
    ├── test_errors_with_mock.py
    └── test_concurrency.py
```

---

## 🧪 Testing

Run all tests:

```bash
pytest -q
```

Key tests:
- **Fuel Types**: CRUD + duplicate (409 conflict).
- **Inventory**: refill, depletion, exact stock checks.
- **Sales**: record sales, insufficient stock (409).
- **Reporting**: revenue, sales by date.
- **Errors**: validation, conflict, internal.
- **Concurrency**: race conditions (simulated).

---

## 📝 Logging

Structured JSON logging (using Python `logging`):

```json
{"level": "INFO", "time": "2025-08-21T06:30:22", "name": "fuel_service", "message": "Creating fuel type name=Diesel price=90.000 stock=500.000"}
```

---

## 🚀 Deployment with Docker

Build and run:

```bash
docker-compose up --build
```

- App: [http://localhost:5050](http://localhost:5050)  
- DB:  [localhost:5432] (user: postgres, pass: postgres)

---

## ✅ Summary

This backend project demonstrates:
- Clean architecture with `src/modules` for business logic.
- SQLAlchemy + migrations for persistence.
- Swagger docs for discoverability.
- Unit & concurrency tests for robustness.
- Structured logging.
- Dockerized, production-ready setup with Gunicorn.
