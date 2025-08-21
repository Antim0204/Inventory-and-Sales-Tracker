from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.models import FuelType
from src.errors import NotFoundError, ValidationError
from src.utils.decimal_utils import to_decimal
from sqlalchemy import text
from src.errors import ConflictError
from src.utils.decimal_utils import to_decimal

def create_fuel_type(session, name, price_per_litre, initial_stock=0):
    name = name.strip()
    price = to_decimal(price_per_litre)
    stock = to_decimal(initial_stock)
    if price < 0 or stock < 0:
        raise ValidationError("price/stock must be >= 0")

    # 1) Pre-check existence by natural key (name)
    exists = session.execute(
        text("SELECT id FROM fuel_types WHERE name = :name"),
        {"name": name}
    ).scalar()

    if exists:
        # Do NOT upsert, do NOT modify existing price/stock here
        raise ConflictError(f'Fuel type "{name}" already exists')

    # 2) Fresh insert (price history + stock set) inside one tx
    row = session.execute(
        text("""
        INSERT INTO fuel_types (name, price_per_litre, stock_litres)
        VALUES (:name, :price, :stock)
        RETURNING id, name, price_per_litre, stock_litres, created_at
        """),
        {"name": name, "price": price, "stock": stock}
    ).mappings().first()

    # 3) Record initial price in history
    session.execute(
        text("""
        INSERT INTO fuel_price_history (fuel_type_id, price_per_litre, valid_from)
        VALUES (:id, :price, NOW())
        """),
        {"id": row["id"], "price": price}
    )

    return {
        "id": row["id"],
        "name": row["name"],
        "price_per_litre": str(row["price_per_litre"]),
        "stock_litres": str(row["stock_litres"]),
        "created_at": row["created_at"],
    }


def update_price(session: Session, fuel_type_id: int, new_price: Decimal) -> dict:
    if new_price < 0:
        raise ValidationError("price must be >= 0")

    # Close open history (if any), then update live price and insert history
    session.execute(
        text("UPDATE fuel_price_history SET valid_to = NOW() WHERE fuel_type_id = :id AND valid_to IS NULL"),
        {"id": fuel_type_id}
    )

    row = session.execute(
        text("""
        UPDATE fuel_types
           SET price_per_litre = :price, updated_at = NOW()
         WHERE id = :id
        RETURNING id, name, price_per_litre, updated_at
        """),
        {"id": fuel_type_id, "price": new_price}
    ).mappings().first()
    if not row:
        raise NotFoundError("fuel type not found")

    session.execute(
        text("INSERT INTO fuel_price_history (fuel_type_id, price_per_litre) VALUES (:id, :price)"),
        {"id": fuel_type_id, "price": new_price}
    )
    return dict(row)

def list_fuel_types(session: Session) -> list[dict]:
    rows = session.execute(
        text("SELECT id, name, price_per_litre FROM fuel_types ORDER BY id")
    ).mappings().all()
    return [dict(r) for r in rows]
