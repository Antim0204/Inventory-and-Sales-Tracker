# src/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv  
load_dotenv()  # Load environment variables from .env file if it exists
@dataclass(frozen=True)
class Settings:
    # Example: postgresql+psycopg://user:pass@localhost:5432/fuel_db
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/fuel_db"
    )
    # Add other knobs here as needed later (e.g., LOG_LEVEL)
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "0") == "1"
    PORT: int = int(os.getenv("PORT", "5000"))
