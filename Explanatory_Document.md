# Inventory and Sales Tracker - Explanatory Document

---

## 📌 Problem Statement

Fuel stations require a reliable backend system to manage:
- Different fuel types (e.g., Petrol, Diesel) with historical prices.
- Inventory levels (stock refills and depletion on sales).
- Sales transactions and revenue reporting.
- Consistency and robustness under concurrent requests.
- Developer-friendly APIs with documentation.
- Production-ready deployment with logging, migrations, and tests.

---

## 🎯 Solution Strategy

We designed a **Flask + PostgreSQL** backend application following **modular architecture**:

1. **Core Requirements**
   - Create and manage **Fuel Types** with price history.
   - Track **Inventory** (refills, consumption).
   - Record **Sales** and generate **Reports**.
   - Provide **Swagger-based docs** for easy exploration.

2. **Architecture**
   - **Flask Blueprints** separate APIs by domain (`fuel_types`, `inventory`, `sales`, `reports`, `meta`).
   - **Service Layer** (`src/modules`) encapsulates business logic.
   - **Models/DB Layer** via SQLAlchemy for persistence.
   - **Error Handling** centralized with custom exceptions (`ConflictError`, `ValidationError`, etc).
   - **Logging** for observability.
   - **Testing**: pytest suite with unit, validation, error, and concurrency cases.
   - **Docker**: Containerized for production deployment.

3. **Scalability**
   - Gunicorn as WSGI server.
   - PostgreSQL ensures ACID compliance.
   - Alembic migrations for schema evolution.

---

## 🧩 Architecture Diagram

👉 **Placeholder for Block Diagram**  
*(Insert your block diagram here – showing API layer → Service layer → DB with arrows for requests, responses, and error handling.)*

---

## 🌐 API Endpoints Overview

### Fuel Types
- `POST /fuel-types` – Create new fuel type.
- `GET /fuel-types` – List all fuel types.
- `PUT /fuel-types/{id}/price` – Update fuel price.

### Inventory
- `POST /inventory/refill` – Refill stock.
- `GET /inventory` – Current inventory snapshot.

### Sales
- `POST /sales` – Record sale.
- `GET /sales` – List sales transactions.

### Reporting
- `GET /reports/sales` – Sales report by date range.
- `GET /reports/revenue` – Revenue report.
- `GET /reports/inventory` – Inventory report.
- `GET /reports/price-history` – Fuel price history.

### Meta
- `GET /health` – Health check.

---

## 🧪 Test Cases

Tests are written using **pytest**.

### Categories:
1. **Fuel Types**
   - Create fuel type.
   - Duplicate fuel type → returns 409.
   - Update price validation.

2. **Inventory**
   - Refill stock.
   - Check stock after refill.
   - Validate negative stock (error).

3. **Sales**
   - Record valid sale.
   - Attempt sale with insufficient stock → 409.
   - Stock depletion verified.

4. **Reporting**
   - Sales report generation.
   - Revenue aggregation.
   - Inventory report.

5. **Errors**
   - ValidationError, NotFoundError, ConflictError responses.
   - Internal errors fallback.

6. **Concurrency**
   - Multiple price updates concurrently.
   - Multiple sales concurrently.
   - Race conditions handled (one wins, others error out gracefully).

---

## 📝 Example Test

```python
class TestDuplicateCreate:
    def test_duplicate_fuel_type_returns_409(self, client):
        r1 = client.post("/fuel-types", json={"name": "Diesel", "price_per_litre": "90.000", "initial_stock_litres":"0.000"})
        assert r1.status_code == 201
        r2 = client.post("/fuel-types", json={"name": "Diesel", "price_per_litre": "95.000", "initial_stock_litres":"100.000"})
        assert r2.status_code == 409
        body = r2.get_json()
        assert body["error"]["code"] == "CONFLICT"
```

---

## ⚙️ Error Handling

- `ValidationError` → 400
- `NotFoundError` → 404
- `ConflictError` → 409
- `InsufficientStockError` → 409
- Fallback unexpected errors → 500

---

## 📂 File Structure Explained

```
.
├── main.py              # App entrypoint
├── src/
│   ├── apis/            # API endpoints
│   ├── modules/         # Business logic
│   ├── models/          # DB models
│   ├── utils/           # Utilities
│   ├── errors.py        # Error classes + handlers
│   └── db.py            # Database session handling
├── sql/                 # Initial schema
├── tests/               # pytest test suite
├── Dockerfile           # Docker build
└── docker-compose.yml   # Compose setup (app + Postgres)
```

---

## 🚀 Deployment Flow

1. **Local**
   - Run with `python main.py`.
   - Swagger: `/apidocs`.

2. **Docker**
   - `docker-compose up --build`
   - Runs app + Postgres in containers.

3. **Production**
   - Gunicorn + Flask app.
   - Logging to stdout (structured).
   - Configurable DB via `.env`.

---

## ✅ Summary

- Clean separation of **API, services, and DB**.
- Robust **error handling** and **logging**.
- Full **test coverage** including concurrency.
- Swagger docs for quick API usage.
- Dockerized deployment with Alembic migrations.

👉 **Placeholder for Additional Diagrams**  
*(Sequence diagrams, request flow, error handling, etc.)*
