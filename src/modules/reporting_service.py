# src/modules/reporting_service.py
from sqlalchemy import text
from sqlalchemy.orm import Session

_GRANULARITIES = {"day": "day", "week": "week", "month": "month"}

def sales_overview(session: Session, start=None, end=None, fuel_type_id=None) -> dict:
    clauses, params = [], {}
    if start: clauses.append("sold_at >= :start"); params["start"] = start
    if end: clauses.append("sold_at <= :end"); params["end"] = end
    if fuel_type_id: clauses.append("fuel_type_id = :ftid"); params["ftid"] = fuel_type_id
    where = "WHERE " + " AND ".join(clauses) if clauses else ""

    # Totals & weighted averages
    q = text(f"""
      SELECT
        COALESCE(SUM(amount),0) AS revenue,
        COALESCE(SUM(litres),0) AS litres,
        COUNT(*) AS tx_count,
        CASE WHEN SUM(litres) > 0 THEN SUM(price_at_sale * litres)/SUM(litres) ELSE 0 END AS weighted_avg_price,
        MIN(sold_at) AS first_sale_at,
        MAX(sold_at) AS last_sale_at
      FROM sales {where}
    """)
    o = session.execute(q, params).mappings().first()

    # Peak & low day by revenue
    q2 = text(f"""
      SELECT date_trunc('day', sold_at) AS d, SUM(amount) AS rev
      FROM sales {where}
      GROUP BY d
      ORDER BY rev DESC
      LIMIT 1
    """)
    peak = session.execute(q2, params).mappings().first()

    q3 = text(f"""
      SELECT date_trunc('day', sold_at) AS d, SUM(amount) AS rev
      FROM sales {where}
      GROUP BY d
      ORDER BY rev ASC
      LIMIT 1
    """)
    low = session.execute(q3, params).mappings().first()

    return {
      "total_revenue": str(o["revenue"]),
      "total_litres": str(o["litres"]),
      "tx_count": int(o["tx_count"]),
      "avg_ticket": (str(o["revenue"]/o["tx_count"]) if o["tx_count"] else "0"),
      "weighted_avg_price": str(o["weighted_avg_price"]),
      "first_sale_at": o["first_sale_at"],
      "last_sale_at": o["last_sale_at"],
      "peak_day": {"date": peak["d"], "revenue": str(peak["rev"])} if peak else None,
      "low_day": {"date": low["d"], "revenue": str(low["rev"])} if low else None,
    }

def sales_timeseries(session: Session, start=None, end=None, fuel_type_id=None, granularity="day") -> list[dict]:
    gran = _GRANULARITIES.get(granularity, "day")
    clauses, params = [], {}
    if start: clauses.append("sold_at >= :start"); params["start"] = start
    if end: clauses.append("sold_at <= :end"); params["end"] = end
    if fuel_type_id: clauses.append("fuel_type_id = :ftid"); params["ftid"] = fuel_type_id
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    q = text(f"""
      SELECT date_trunc('{gran}', sold_at) AS bucket,
             SUM(amount) AS revenue,
             SUM(litres) AS litres,
             COUNT(*) AS tx_count,
             AVG(price_at_sale) AS avg_price
        FROM sales {where}
    GROUP BY bucket
    ORDER BY bucket
    """)
    rows = session.execute(q, params).mappings().all()
    return [{"period_start": r["bucket"], "revenue": str(r["revenue"]), "litres": str(r["litres"]),
             "tx_count": int(r["tx_count"]), "avg_price": str(r["avg_price"])} for r in rows]

def sales_by_fuel_type(session: Session, start=None, end=None) -> list[dict]:
    clauses, params = [], {}
    if start: clauses.append("s.sold_at >= :start"); params["start"] = start
    if end: clauses.append("s.sold_at <= :end"); params["end"] = end
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    q = text(f"""
      SELECT s.fuel_type_id, ft.name,
             SUM(s.amount) AS revenue,
             SUM(s.litres) AS litres,
             COUNT(*) AS tx_count,
             AVG(s.price_at_sale) AS avg_price
        FROM sales s
        JOIN fuel_types ft ON ft.id = s.fuel_type_id
        {where}
    GROUP BY s.fuel_type_id, ft.name
    ORDER BY revenue DESC
    """)
    rows = session.execute(q, params).mappings().all()
    return [{"fuel_type_id": r["fuel_type_id"], "name": r["name"],
             "revenue": str(r["revenue"]), "litres": str(r["litres"]),
             "tx_count": int(r["tx_count"]), "avg_price": str(r["avg_price"])} for r in rows]

def price_history(session: Session, fuel_type_id: int, start=None, end=None) -> list[dict]:
    # Return price segments overlapping the range
    clauses = ["fuel_type_id = :ftid"]; params = {"ftid": fuel_type_id}
    if start: clauses.append("(valid_to IS NULL OR valid_to >= :start)"); params["start"] = start
    if end: clauses.append("valid_from <= :end"); params["end"] = end
    where = "WHERE " + " AND ".join(clauses)
    q = text(f"""
      SELECT price_per_litre, valid_from, valid_to
        FROM fuel_price_history
        {where}
    ORDER BY valid_from
    """)
    rows = session.execute(q, params).mappings().all()
    return [{"price_per_litre": str(r["price_per_litre"]),
             "valid_from": r["valid_from"], "valid_to": r["valid_to"]} for r in rows]
