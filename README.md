# **Fuel Station Inventory & Sales Tracker**

This document provides a comprehensive overview and setup guide for a production-ready backend system designed to manage a fuel station's inventory, sales, and reporting. The application is built with a modular architecture to ensure scalability, maintainability, and robustness.

## **📌 Problem Statement**

The system addresses the core needs of a fuel station, including:

* Managing different fuel types with historical pricing.  
* Tracking inventory levels and handling refills and sales-based depletion.  
* Recording sales transactions and generating detailed revenue reports.  
* Ensuring data consistency and handling concurrent requests gracefully.  
* Providing a well-documented, developer-friendly set of APIs.

## **🎯 Solution Strategy & Architecture**

The solution is a **Flask \+ PostgreSQL** backend application. It follows a modular design with a clear separation of concerns, organized into the following layers:

* **API Layer (src/apis):** Implemented using **Flask Blueprints** to separate endpoints by domain (e.g., fuel\_types, inventory, sales). It handles request parsing and delegates business logic to the service layer.  
* **Service Layer (src/modules):** Encapsulates all business logic, such as validating a sale, calculating revenue, or updating stock levels.  
* **Database (DB) Layer (src/models, src/db):** Uses **SQLAlchemy** for object-relational mapping (ORM), providing an abstraction over the PostgreSQL database. **Alembic** is used for database migrations, allowing for smooth schema evolution.  
* **Error Handling (src/errors.py):** Centralized error handling using custom exceptions (ValidationError, ConflictError, InsufficientStockError) to return appropriate HTTP status codes.  
* **Testing (tests):** A comprehensive test suite using **pytest** covers unit tests, validation, error handling, and concurrency simulations to ensure system robustness.  
* **Deployment:** The application is **containerized with Docker** for easy, consistent deployment across environments.

## **🛠️ Tech Stack**

* **Backend Framework:** Python 3.10, Flask 3.x  
* **Database:** PostgreSQL 15  
* **ORM/Migrations:** SQLAlchemy 2.x, Alembic  
* **API Documentation:** Flasgger (provides interactive Swagger UI at /apidocs)  
* **Testing:** pytest  
* **Containerization:** Docker, docker-compose  
* **Configuration:** python-dotenv

## **⚙️ Setup Instructions**

### **1\. Install Dependencies**

First, clone the project repository and set up a Python virtual environment.

git clone \<repo-url\>  
cd Inventory-and-Sales-Tracker  
python3 \-m venv .venv  
source .venv/bin/activate    \# macOS/Linux  
\# .venv\\\\Scripts\\\\activate     \# Windows  
pip install \-r requirements.txt

### **2\. Setup PostgreSQL Database**

This step is critical for the application to function. You will create the necessary user role, the database, and load the initial schema.

\# Install PostgreSQL (if not already installed)  
brew install postgresql@15  \# For macOS

\# Start the PostgreSQL service  
brew services start postgresql@15

\# Create a 'postgres' role and a 'fuel\_db' database  
psql \-d postgres \-c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';"  
createdb \-U postgres fuel\_db

### **3\. Load Initial Schema**

The initial database schema is defined in sql/001\_init.sql. You must load this schema to create the necessary tables.

psql "postgresql://postgres:postgres@localhost:5432/fuel\_db" \-f sql/001\_init.sql

### **4\. Configure Environment Variables**

Create a .env file in the project's root directory and populate it with your database connection details.

DATABASE\_URL=postgresql+psycopg://postgres:postgres@db:5432/fuel\_db  
FLASK\_DEBUG=0  
PORT=5050  
POSTGRES\_USER=postgres  
POSTGRES\_PASSWORD=postgres  
POSTGRES\_DB=fuel\_db

### **5. Run the Application**

**Recommended:** Run with Docker Compose. You do **not** need to install PostgreSQL locally — the `db` service runs Postgres in a container and initializes the schema from `./sql/001_init.sql`. Your app connects to this in-network DB; no local Postgres install is required.

```bash
# macOS/Linux
docker compose build --no-cache     # or: docker-compose build --no-cache
docker compose up                   # or: docker-compose up

# Windows (PowerShell)
# docker compose build --no-cache
# docker compose up
```

Now open **http://localhost:5050/apidocs**.

To stop:
```bash
# macOS/Linux
docker compose down                 # or: docker-compose down

# Windows (PowerShell)
# docker compose down
```

---

**Alternative:** Run locally via Python (requires a local Python toolchain; Postgres can still be in Docker or external).
See **Step 6** below for OS-specific Python commands.

### **6. Run Locally via Python (Alternative)**

You can also run the app without containers. Create a virtualenv and start the app:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional if not using .env
export PORT=5050

python main.py

# Windows (PowerShell)
# py -m venv .venv
# .\.venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# $env:PORT = "5050"
# python .\main.py
```

> Tip: Even when running via Python locally, you can still use the Dockerized Postgres by keeping `DATABASE_URL` pointing at `db:5432` **from within containers** or `localhost:5432` **if you expose and run Postgres locally/Docker with published port**.

## **🌐 API Endpoints**

The API is structured around core business functions and returns JSON for all requests.

| Endpoint | Method | Description |
| :---- | :---- | :---- |
| /fuel-types | POST, GET | Create a new fuel type or list all existing fuel types. |
| /fuel-types/{id}/price | PATCH | Update the price of a specific fuel type. |
| /inventory/refill | POST | Add stock to a fuel type. |
| /inventory | GET | Get a snapshot of the current inventory levels. |
| /sales | POST, GET | Record a new sale or list past sales transactions. |
| /reports/sales/overview | GET | Get key sales metrics. |
| /reports/sales/timeseries | GET | Get sales data aggregated over time. |
| /reports/sales/by-fuel-type | GET | Get sales metrics grouped by fuel type. |
| /reports/price/history | GET | View the price history for a fuel type. |
| /health | GET | A simple health check endpoint. |

## **📚 Detailed API Documentation**

Here is a more detailed look at the key API endpoints with example curl commands. The examples assume the app is running locally on port 5050\.

### **Fuel Types**

#### **1\. Create a New Fuel Type**

* **Description:** Creates a new fuel type with an initial price and stock.  
* **Method & Path:** POST /fuel-types  
* **Request Body:**  
  {  
    "name": "Diesel",  
    "price\_per\_litre": "90.000",  
    "initial\_stock\_litres": "500.000"  
  }  
* **curl Example:**  
  curl \-X POST http://localhost:5050/fuel-types \\  
    \-H 'Content-Type: application/json' \\  
    \-d '{"name":"Diesel","price\_per\_litre":"90.000","initial\_stock\_litres":"500.000"}'

#### **2\. Get All Fuel Types**

* **Description:** Retrieves a list of all fuel types currently in the system.  
* **Method & Path:** GET /fuel-types  
* **curl Example:**  
  curl http://localhost:5050/fuel-types

#### **3\. Update Fuel Price**

* **Description:** Updates the price per litre for a specific fuel type. A new price history entry is created.  
* **Method & Path:** PATCH /fuel-types/{id}/price (e.g., /fuel-types/1/price)  
* **Request Body:**  
  {  
    "price\_per\_litre": "92.500"  
  }  
* **curl Example:**  
  curl \-X PUT http://localhost:5050/fuel-types/1/price \\  
    \-H 'Content-Type: application/json' \\  
    \-d '{"price\_per\_litre":"92.500"}'

### **Inventory**

#### **1\. Refill Stock**

* **Description:** Adds a specified amount of fuel to the inventory of a given fuel type.  
* **Method & Path:** POST /inventory/refill  
* **Request Body:**  
  {  
    "fuel\_type\_id": 1,  
    "litres": "100.000"  
  }  
* **curl Example:**  
  curl \-X POST http://localhost:5050/inventory/refill \\  
    \-H 'Content-Type: application/json' \\  
    \-d '{"fuel\_type\_id":1,"litres":"100.000"}'

#### **2\. Get Current Inventory**

* **Description:** Retrieves the current stock levels for all fuel types.  
* **Method & Path:** GET /inventory  
* **curl Example:**  
  curl http://localhost:5050/inventory

### **Sales**

#### **1\. Record a Sale**

* **Description:** Records a sale transaction, automatically deducting the sold amount from the inventory and calculating the total revenue based on the current price. It will fail with a 409 Conflict if there is insufficient stock.  
* **Method & Path:** POST /sales  
* **Request Body:**  
  {  
    "fuel\_type\_id": 1,  
    "litres": "50.000"  
  }  
* **curl Example:**  
  curl \-X POST http://localhost:5050/sales \\  
    \-H 'Content-Type: application/json' \\  
    \-d '{"fuel\_type\_id":1,"litres":"50.000"}'

#### **2\. Get Sales History**

* **Description:** Retrieves a list of all sales transactions. This endpoint can be filtered by a date range and/or a specific fuel type.  
* **Method & Path:** GET /sales  
* **URL Parameters:** from, to (date strings in YYYY-MM-DD format), fuel\_type\_id (integer).  
* **curl Example:**  
  curl "http://localhost:5050/sales?from=2025-08-01\&to=2025-08-20\&fuel\_type\_id=1"

### **Reporting**

#### **1\. Sales Overview**

* **Description:** Provides a summary of key sales metrics over a specified period. Useful for a quick glance at overall performance.  
* **Method & Path:** GET /reports/sales/overview  
* **URL Parameters:** from, to (optional date strings), fuel\_type\_id (optional integer).  
* **curl Example:**  
  \# Get sales overview for a specific date range  
  curl "http://localhost:5050/reports/sales/overview?from=2025-08-01\&to=2025-08-20"

  \# Get sales overview for a specific fuel type in a date range  
  curl "http://localhost:5050/reports/sales/overview?from=2025-08-01\&to=2025-08-20\&fuel\_type\_id=1"

#### **2\. Sales Time Series**

* **Description:** Aggregates sales data over time, allowing for the creation of charts and trend analysis.  
* **Method & Path:** GET /reports/sales/timeseries  
* **URL Parameters:** from, to, fuel\_type\_id (all optional), granularity (optional; day, week, or month).  
* **curl Example:**  
  \# Get daily sales data  
  curl "http://localhost:5050/reports/sales/timeseries?granularity=day"

  \# Get weekly sales data for a specific fuel type  
  curl "http://localhost:5050/reports/sales/timeseries?granularity=week\&fuel\_type\_id=1"

#### **3\. Sales by Fuel Type**

* **Description:** Breaks down total sales by each fuel type, making it easy to see which products are most popular.  
* **Method & Path:** GET /reports/sales/by-fuel-type  
* **URL Parameters:** from, to (optional date strings).  
* **curl Example:**  
  \# Get a breakdown of sales by fuel type for the current month  
  curl "http://localhost:5050/reports/sales/by-fuel-type"

  \# Get sales grouped by fuel type for a specific period  
  curl "http://localhost:5050/reports/sales/by-fuel-type?from=2025-01-01\&to=2025-12-31"

#### 

#### **4\. Price History**

* **Description:** Retrieves the price history for a single fuel type, showing every price change over time.  
* **Method & Path:** GET /reports/price/history  
* **URL Parameters:** fuel\_type\_id (required integer), from, to (optional date strings).  
* **curl Example:**  
  \# Get all price history for fuel type with ID 1  
  curl "http://localhost:5050/reports/price/history?fuel\_type\_id=1"

  \# Get price history for fuel type 1 within a specific date range  
  curl "http://localhost:5050/reports/price/history?fuel\_type\_id=1\&from=2025-07-01\&to=2025-09-30"



## **📂 Project Structure**

![][image1]

## **🚀 Deployment**

The project is designed for easy deployment using Docker. The docker-compose.yml file sets up both the Flask application and a PostgreSQL container.

To build and run the application using Docker, simply use the following command:

docker-compose up \--build

To stop the containers and remove them, use:

docker-compose down

The application will be accessible at http://localhost:5050 and the database at localhost:5332.

[image1]: <data:image/png;base64,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>

## 🗄️ Database Schema Explanation

The initial database schema (`sql/001_init.sql`) defines the core entities for managing fuel inventory and sales【8†source】:

### **1. fuel_types**
Stores the available fuel types along with their current price and stock.
- **id**: Primary key (unique identifier for each fuel type).
- **name**: Unique name of the fuel type (e.g., Petrol, Diesel).
- **price_per_litre**: Current price per litre (must be non-negative).
- **stock_litres**: Current stock available in litres (default is 0, must be non-negative).
- **created_at / updated_at**: Timestamps for auditing.

### **2. fuel_price_history**
Keeps a record of historical price changes for auditing and reporting.
- **id**: Primary key.
- **fuel_type_id**: Foreign key referencing `fuel_types`.
- **price_per_litre**: Price at that point in time.
- **valid_from / valid_to**: Time range for which the price was valid.
- **Index**: Added on `fuel_type_id` for faster queries.

### **3. sales**
Immutable records of every sale transaction.
- **id**: Primary key.
- **fuel_type_id**: Foreign key referencing `fuel_types`.
- **litres**: Number of litres sold (must be > 0).
- **price_at_sale**: The fuel price per litre at the time of sale.
- **amount**: Total sale amount (litres × price_at_sale).
- **sold_at**: Timestamp of when the sale occurred.
- **Indexes**: On `sold_at` and `fuel_type_id` for efficient reporting.

Together, these tables ensure we can:
- Track live inventory.
- Record sales immutably.
- Maintain historical prices for reporting and auditing.

## 🐳 Docker Setup Explanation

The `docker-compose.yml` file defines two main services【10†source】:

### **1. db (PostgreSQL 15)**
- **Image**: Uses the official `postgres:15` image.
- **Environment Variables**: Loaded from `.env` file.
- **Volumes**:
  - `db_data:/var/lib/postgresql/data`: Persists database data between container restarts.
  - `./sql:/docker-entrypoint-initdb.d:ro`: Mounts the SQL schema for automatic initialization.
- **Ports**: Maps host `5432` to container `5432` for database access.

### **2. app (Flask Application)**
- **Build**: Built from the local Dockerfile in the project root.
- **Depends_on**: Ensures `db` starts before the app.
- **Environment Variables**: Loaded from `.env` file.
- **Ports**: Maps host `5050` to container `5050` (application available at `http://localhost:5050`).
- **Volumes**:
  - `.:/app:cached`: Mounts local project directory into container (live code reload).
- **Command**: Runs the app with Gunicorn (`gunicorn -w 4 -b 0.0.0.0:${PORT} main:app`).

### **Volumes**
- `db_data`: A named Docker volume for persisting Postgres data.

This setup ensures:
- **App and DB run in isolated containers.**
- **Database schema auto-initializes** from the mounted `sql` folder.
- **Hot reload for development** using project directory volume mount.

## 🧪 Running Unit Tests with Docker

The application includes a test suite written in **pytest**.  
We run tests inside the Dockerized environment to ensure consistent results.

### **1. Create Test Database**
```bash
docker compose exec -T db psql -U postgres -d postgres -c "CREATE DATABASE fuel_db_test;"
docker compose exec -T db psql -U postgres -d fuel_db_test -f /docker-entrypoint-initdb.d/001_init.sql
```

### **2. Run Tests**
```bash
docker compose run --rm   -e DATABASE_URL='postgresql+psycopg://postgres:postgres@db:5432/fuel_db_test'   app sh -lc '
    pytest -q       --maxfail=1 --disable-warnings       --cov=src       --cov-report=term-missing       --cov-report=html:coverage_html       --cov-report=xml:coverage.xml       --junitxml=pytest-report.xml
  '
```

### **3. Coverage Reports**
- Results are shown **in the terminal**.
- Coverage reports are also stored in the **project root**:
  - `coverage_html/`: Open `index.html` in a browser for a detailed view.
  - `coverage.xml`: XML coverage format (for CI tools).
  - `pytest-report.xml`: Test report in JUnit format.

This setup ensures **tests run against an isolated test DB** inside Docker.

## 📬 Postman Examples

While curl commands are provided above【9†source】, you can also use **Postman** for testing.

### **1. Create Fuel Type**
- **Method:** POST  
- **URL:** http://localhost:5050/fuel-types  
- **Body (JSON):**
```json
{
  "name": "Diesel",
  "price_per_litre": "90.000",
  "initial_stock_litres": "500.000"
}
```

### **2. Record a Sale**
- **Method:** POST  
- **URL:** http://localhost:5050/sales  
- **Body (JSON):**
```json
{
  "fuel_type_id": 1,
  "litres": "50.000"
}
```

### **3. Get Sales Overview**
- **Method:** GET  
- **URL:** http://localhost:5050/reports/sales/overview?from=2025-08-01&to=2025-08-20  

### **4. Health Check**
- **Method:** GET  
- **URL:** http://localhost:5050/health  

💡 Tip: Import the collection of these requests into Postman for easy reuse.

## 🛑 Docker Commands Reference

### **Start Application**
```bash
docker-compose build --no-cache
docker-compose up
```

### **Stop Application**
```bash
docker-compose down
```

### **Clean Resources**
```bash
docker images
docker rmi <image_id>         # Remove images
docker system prune           # Clean unused resources (type 'y' when prompted)
```

## 🧰 Installing Docker & Docker Compose

> Compose v2 ships with Docker Desktop on macOS/Windows and as a plugin on Linux. The command is `docker compose ...` (space), but `docker-compose` also works in many setups.

### macOS
- **Docker Desktop (recommended):**
  ```bash
  brew install --cask docker
  # After install, launch Docker.app once so the Docker daemon starts
  docker compose version
  ```

### Windows
- **Docker Desktop (recommended via Winget):**
  ```powershell
  winget install --id Docker.DockerDesktop -e
  # After install, start Docker Desktop, then verify:
  docker compose version
  ```

### Linux (Debian/Ubuntu)
- **Engine + Compose plugin:**
  ```bash
  sudo apt-get update
  sudo apt-get install -y docker.io docker-compose-plugin
  sudo usermod -aG docker "$USER"  # log out/in to apply group
  docker compose version
  ```

### Linux (RHEL/CentOS/Fedora)
```bash
sudo dnf install -y docker docker-compose-plugin
sudo usermod -aG docker "$USER"
docker compose version
```


