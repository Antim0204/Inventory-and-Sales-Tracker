# scripts/bootstrap_db.py
import os
from sqlalchemy import create_engine
from src.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/fuel_db")

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Tables created.")
