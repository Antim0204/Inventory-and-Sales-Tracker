# tests/conftest.py
import os
import pathlib
import pytest
from flask import Flask
from sqlalchemy import create_engine, text

from src import create_app

SQL_PATH = str(pathlib.Path(__file__).resolve().parents[1] / "sql" / "001_init.sql")

def _bootstrap_schema(database_url: str):
    """
    Execute the DDL file directly via SQLAlchemy/psycopg.
    Avoids requiring `psql` inside the app container.
    Safe to run multiple times (your SQL is idempotent with IF NOT EXISTS).
    """
    engine = create_engine(database_url, future=True)
    ddl = pathlib.Path(SQL_PATH).read_text(encoding="utf-8")
    # exec_driver_sql allows multiple semicolon-separated statements
    with engine.begin() as conn:
        conn.exec_driver_sql(ddl)

@pytest.fixture(scope="session")
def app() -> Flask:
    app = create_app()

    # Ensure we point at the test DB
    db_url = app.config["SETTINGS"].DATABASE_URL
    # If your runtime URL is postgresql+psycopg://... keep it as-is.
    # No need to strip +psycopg; SQLAlchemy understands it.

    # Bootstrap schema without calling external psql
    _bootstrap_schema(db_url)

    return app


@pytest.fixture(autouse=True)
def clean_db(app):
    """Truncate all domain tables before each test and reset identities."""
    db_url = app.config["SETTINGS"].DATABASE_URL
    engine = create_engine(db_url, future=True)
    with engine.begin() as conn:
        # Order doesn’t matter with TRUNCATE ... CASCADE, but we reset IDs.
        conn.exec_driver_sql("""
            TRUNCATE TABLE
              sales,
              fuel_price_history,
              fuel_types
            RESTART IDENTITY CASCADE;
        """)

@pytest.fixture(scope="session", autouse=True)
def wipe_once(app):
    db_url = app.config["SETTINGS"].DATABASE_URL
    engine = create_engine(db_url, future=True)
    with engine.begin() as conn:
        conn.exec_driver_sql("""
            TRUNCATE TABLE
              sales,
              fuel_price_history,
              fuel_types
            RESTART IDENTITY CASCADE;
        """)



@pytest.fixture()
def client(app):
    return app.test_client()

