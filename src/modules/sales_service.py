from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.errors import NotFoundError, InsufficientStockError, ValidationError

def record_sale(session: Session, fuel_type_id: int, litres: Decimal) -> dict:
    if litres <= 0:
        raise ValidationError("litres must be > 0")

    # Atomic stock decrement + sale insert; fails if insufficient stock
    row = session.execute(
        text("""
        WITH updated AS (
          UPDATE fuel_types
             SET stock_litres = stock_litres - :litres,
                 updated_at = NOW()
           WHERE id = :fuel_type_id
             AND stock_litres >= :litres
          RETURNING id, price_per_litre
        )
        INSERT INTO sales (fuel_type_id, litres, price_at_sale, amount)
        SELECT id, :litres, price_per_litre, (:litres * price_per_litre)
          FROM updated
        RETURNING id, fuel_type_id, litres, price_at_sale, amount, sold_at
        """),
        {"fuel_type_id": fuel_type_id, "litres": litres}
    ).mappings().first()

    if not row:
        exists = session.execute(text("SELECT 1 FROM fuel_types WHERE id = :id"), {"id": fuel_type_id}).first()
        if not exists:
            raise NotFoundError("fuel type not found")
        raise InsufficientStockError("insufficient stock")

    return dict(row)

def list_sales(session: Session, start=None, end=None, fuel_type_id=None) -> list[dict]:
    clauses = []
    params = {}
    if start:
        clauses.append("sold_at >= :start"); params["start"] = start
    if end:
        clauses.append("sold_at <= :end"); params["end"] = end
    if fuel_type_id:
        clauses.append("fuel_type_id = :ftid"); params["ftid"] = fuel_type_id

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = session.execute(
        text(f"SELECT id, fuel_type_id, litres, price_at_sale, amount, sold_at FROM sales {where} ORDER BY sold_at DESC"),
        params
    ).mappings().all()
    return [dict(r) for r in rows]
