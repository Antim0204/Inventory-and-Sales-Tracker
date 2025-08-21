from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.errors import NotFoundError, ValidationError

def refill_stock(session: Session, fuel_type_id: int, litres: Decimal) -> dict:
    if litres <= 0:
        raise ValidationError("litres must be > 0")
    row = session.execute(
        text("""
        UPDATE fuel_types
           SET stock_litres = stock_litres + :litres, updated_at = NOW()
         WHERE id = :id
        RETURNING id, stock_litres
        """),
        {"id": fuel_type_id, "litres": litres}
    ).mappings().first()
    if not row:
        raise NotFoundError("fuel type not found")
    return {"fuel_type_id": row["id"], "new_stock_litres": row["stock_litres"]}

def list_inventory(session: Session) -> list[dict]:
    rows = session.execute(
        text("SELECT id AS fuel_type_id, name, stock_litres FROM fuel_types ORDER BY id")
    ).mappings().all()
    return [dict(r) for r in rows]
