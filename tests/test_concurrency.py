# tests/test_concurrency.py
from decimal import Decimal
import threading
from queue import Queue
import time

from sqlalchemy import text

# We’ll call the service directly (not Flask test client) to avoid client thread issues.
from src.modules.fuel_types_service import create_fuel_type
from src.modules.sales_service import record_sale, InsufficientStockError
from src.db import session_scope

class TestConcurrentSales:
    def _sale_worker(self, session_factory, fuel_type_id, litres, out_q):
        """Each worker uses its own DB session; captures (ok, payload_or_exc)."""
        try:
            with session_scope(session_factory) as s:
                res = record_sale(s, fuel_type_id, Decimal(litres))
                out_q.put((True, res))
        except Exception as e:
            out_q.put((False, e))

    def test_two_competing_sales_one_wins(self, app):
        """
        Stock=60; two threads try to sell 50L each ⇒ exactly one should succeed, one fail (insufficient stock).
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "Diesel", Decimal("90.000"), Decimal("60.000"))
            fuel_type_id = ft["id"]

        out = Queue()
        t1 = threading.Thread(target=self._sale_worker, args=(sf, fuel_type_id, "50.000", out))
        t2 = threading.Thread(target=self._sale_worker, args=(sf, fuel_type_id, "50.000", out))

        # Start “together”
        t1.start(); t2.start()
        t1.join(); t2.join()

        results = [out.get(), out.get()]
        successes = [r for r in results if r[0]]
        failures  = [r for r in results if not r[0]]

        assert len(successes) == 1, f"Expected 1 success, got: {results}"
        assert len(failures) == 1, f"Expected 1 failure, got: {results}"
        assert isinstance(failures[0][1], InsufficientStockError)

        # Verify final stock is 10 (= 60 - 50) and only 1 sale row exists
        with session_scope(sf) as s:
            row = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fuel_type_id}).first()
            assert row and row[0] == Decimal("10.000")
            cnt = s.execute(text("SELECT COUNT(*) FROM sales WHERE fuel_type_id=:id"), {"id": fuel_type_id}).scalar()
            assert cnt == 1

    def test_many_parallel_sales_total_never_exceeds_stock(self, app):
        """
        Stock=100; ten threads attempt 15L each (total demand=150) ⇒ at most floor(100/15)=6 succeed.
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "Petrol", Decimal("100.000"), Decimal("100.000"))
            fuel_type_id = ft["id"]

        out = Queue()
        threads = []
        for _ in range(10):
            t = threading.Thread(target=self._sale_worker, args=(sf, fuel_type_id, "15.000", out))
            threads.append(t)

        for t in threads: t.start()
        for t in threads: t.join()

        results   = [out.get() for _ in threads]
        successes = [r for r in results if r[0]]
        failures  = [r for r in results if not r[0]]

        # At most 6 can succeed (6*15=90 <= 100, 7th would push to 105)
        assert 0 < len(successes) <= 6
        assert len(successes) + len(failures) == 10
        assert all(isinstance(f[1], InsufficientStockError) for f in failures)

        with session_scope(sf) as s:
            sold_litres = s.execute(
                text("SELECT COALESCE(SUM(litres), 0) FROM sales WHERE fuel_type_id=:id"),
                {"id": fuel_type_id}
            ).scalar()
            # Never exceeds initial stock
            assert sold_litres <= Decimal("100.000")
            stock = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fuel_type_id}).scalar()
            assert stock == Decimal("100.000") - sold_litres

    def test_exact_split_parallel_both_succeed(self, app):
        """
        Stock=100; two threads sell 50L each ⇒ both succeed and stock ends at 0.
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "XPremium", Decimal("120.000"), Decimal("100.000"))
            fuel_type_id = ft["id"]

        out = Queue()
        t1 = threading.Thread(target=self._sale_worker, args=(sf, fuel_type_id, "50.000", out))
        t2 = threading.Thread(target=self._sale_worker, args=(sf, fuel_type_id, "50.000", out))
        t1.start(); t2.start(); t1.join(); t2.join()

        results   = [out.get(), out.get()]
        successes = [r for r in results if r[0]]

        assert len(successes) == 2, f"Both should succeed, got: {results}"

        with session_scope(sf) as s:
            stock = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fuel_type_id}).scalar()
            assert stock == Decimal("0.000")
            cnt = s.execute(text("SELECT COUNT(*) FROM sales WHERE fuel_type_id=:id"), {"id": fuel_type_id}).scalar()
            assert cnt == 2
