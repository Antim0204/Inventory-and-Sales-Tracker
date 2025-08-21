# Fuel Station Inventory & Sales Tracker

Backend service to manage daily operations of a fuel station.

## 🚀 Tech Stack
- Python (Flask)
- PostgreSQL
- SQLAlchemy + Alembic (migrations)
- Marshmallow (validation)

Optional:
- Docker (future)
- Reporting API
- Unit tests

---

## 📌 Features
- **Fuel Types**
  - Add new fuel types
  - Update price
  - List all fuel types
- **Inventory**
  - Refill stock
  - View current stock levels
- **Sales**
  - Record a sale (deduct stock, prevent overselling)
  - Calculate amount = litres × current price
  - Retrieve sales history

All rules and validations enforced (price ≥ 0, litres > 0, block sale if insufficient stock).

---

## ⚙️ Setup Instructions

### 1. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Setup PostgreSQL
```bash
brew install postgresql@15
brew services start postgresql@15

# create role + db (if not already created)
psql -d postgres -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';"
createdb -U postgres fuel_db
```

### 3. Load schema
```bash
psql "postgresql://postgres:postgres@localhost:5432/fuel_db" -f sql/001_init.sql
```

### 4. Run app
```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/fuel_db"
python main.py
```

App runs at: `http://localhost:5000`

---

## 📬 Example API Calls

```bash
# Create fuel type
curl -X POST http://localhost:5000/fuel-types \
  -H 'Content-Type: application/json' \
  -d '{"name":"Diesel","price_per_litre":"90.000","initial_stock_litres":"500.000"}'

# Update price
curl -X PATCH http://localhost:5000/fuel-types/1/price \
  -H 'Content-Type: application/json' \
  -d '{"price_per_litre":"92.500"}'

# Refill stock
curl -X POST http://localhost:5000/inventory/refill \
  -H 'Content-Type: application/json' \
  -d '{"fuel_type_id":1,"litres":"100.000"}'

# Record a sale
curl -X POST http://localhost:5000/sales \
  -H 'Content-Type: application/json' \
  -d '{"fuel_type_id":1,"litres":"50.000"}'

# Get sales history
curl "http://localhost:5000/sales?from=2025-08-01&to=2025-08-20&fuel_type_id=1"
```

---

## 🧪 Tests
We will add unit tests in the `tests/` folder (using `pytest` or `unittest`).  
Run with:
```bash
pytest
```

---

## 📊 Interactive API Docs

Unlike FastAPI, Flask doesn’t ship with `/docs` by default.  
To get Swagger-UI / ReDoc:

- **Option A (Flasgger)**  
  ```bash
  pip install flasgger
  ```
  Then in `src/__init__.py`:
  ```python
  from flasgger import Swagger
  def create_app():
      app = Flask(__name__)
      Swagger(app)   # auto serves docs at /apidocs
      ...
      return app
  ```
  Open: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

- **Option B (flask-swagger-ui)**  
  Lets you mount a `/docs` endpoint serving an OpenAPI spec.

Either way, you’ll get **interactive docs similar to FastAPI**.  

---

## 📂 Deliverables
- Source code under `src/`
- `requirements.txt`
- `sql/001_init.sql` schema
- README.md (this file)
