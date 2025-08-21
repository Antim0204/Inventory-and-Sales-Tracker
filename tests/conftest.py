# tests/conftest.py
import os
import subprocess
import pytest
from dotenv import load_dotenv
from flask import Flask

# Load test env before importing app
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env.test"), override=True)

from src import create_app 

SQL_PATH = os.path.join(os.getcwd(), "sql", "001_init.sql")

@pytest.fixture(scope="session")
def app() -> Flask:
    app = create_app()
    # Ensure schema is present in the test DB (idempotent SQL)
    db_url = app.config["SETTINGS"].DATABASE_URL.replace("+psycopg", "")
    subprocess.run(
        ["psql", db_url, "-f", SQL_PATH],
        check=True
    )
    return app

@pytest.fixture(autouse=True)
def clean_db(app: Flask):
    """Truncate tables before each test for isolation."""
    from sqlalchemy import text
    sf = app.config["SESSION_FACTORY"]
    with sf() as s:
        s.execute(text("TRUNCATE TABLE sales RESTART IDENTITY CASCADE;"))
        s.execute(text("TRUNCATE TABLE fuel_price_history RESTART IDENTITY CASCADE;"))
        s.execute(text("TRUNCATE TABLE fuel_types RESTART IDENTITY CASCADE;"))
        s.commit()
    yield

@pytest.fixture()
def client(app: Flask):
    return app.test_client()
