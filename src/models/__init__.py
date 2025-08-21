from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Re-export entities for easy imports
from src.models.entities import FuelType, FuelPriceHistory, Sale  # noqa: E402,F401
