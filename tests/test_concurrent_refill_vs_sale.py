from decimal import Decimal
import threading
from queue import Queue
from time import sleep

from sqlalchemy import text
from src.db import session_scope
from src.modules.fuel_types_service import create_fuel_type
from src.modules.inventory_service import refill_stock
from src.modules.sales_service import record_sale, InsufficientStockError

class TestRefillVsSaleConcurrency:
    def _sale_worker(self, session_factory, fuel_type_id, litres, out_q, delay=0.0):
        try:
            if delay:
                sleep(delay)
            with session_scope(session_factory) as s:
                sale = record_sale(s, fuel_type_id, Decimal(litres))
                out_q.put(("sale_ok", sale))
        except Exception as e:
            out_q.put(("sale_err", e))

    def _refill_worker(self, session_factory, fuel_type_id, litres, out_q, delay=0.0):
        try:
            if delay:
                sleep(delay)
            with session_scope(session_factory) as s:
                res = refill_stock(s, fuel_type_id, Decimal(litres))
                out_q.put(("refill_ok", res))
        except Exception as e:
            out_q.put(("refill_err", e))

    def test_refill_happens_before_sale_sale_succeeds(self, app):
        """
        Start with stock=50. Refill +20 then sell 60.
        Refill commits first → sale sees 70 available → sale succeeds → final stock = 10.
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "RefillWins", Decimal("90.000"), Decimal("50.000"))
            fid = ft["id"]

        q = Queue()
        t_refill = threading.Thread(target=self._refill_worker, args=(sf, fid, "20.000", q, 0.00))
        t_sale   = threading.Thread(target=self._sale_worker,   args=(sf, fid, "60.000", q, 0.02))  # sale slightly delayed

        t_refill.start(); t_sale.start()
        t_refill.join();  t_sale.join()

        results = [q.get(), q.get()]
        # Expect: one refill_ok, one sale_ok
        assert any(r[0] == "refill_ok" for r in results)
        assert any(r[0] == "sale_ok" for r in results)

        with session_scope(sf) as s:
            stock = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fid}).scalar()
            assert stock == Decimal("10.000")  # 50 + 20 - 60
            cnt = s.execute(text("SELECT COUNT(*) FROM sales WHERE fuel_type_id=:id"), {"id": fid}).scalar()
            assert cnt == 1

    def test_sale_attempts_before_refill_sale_fails_then_refill_commits(self, app):
        """
        Start with stock=50. Attempt to sell 60 first → insufficient → failure.
        Then refill +20 commits → final stock = 70 (no sale recorded).
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "SaleFirst", Decimal("90.000"), Decimal("50.000"))
            fid = ft["id"]

        q = Queue()
        t_sale   = threading.Thread(target=self._sale_worker,   args=(sf, fid, "60.000", q, 0.00))
        t_refill = threading.Thread(target=self._refill_worker, args=(sf, fid, "20.000", q, 0.02))  # refill delayed

        t_sale.start(); t_refill.start()
        t_sale.join();  t_refill.join()

        results = [q.get(), q.get()]
        # Expect: sale_err (InsufficientStockError) and refill_ok
        sale_err = next((r for r in results if r[0] == "sale_err"), None)
        assert sale_err and isinstance(sale_err[1], InsufficientStockError)
        assert any(r[0] == "refill_ok" for r in results)

        with session_scope(sf) as s:
            stock = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fid}).scalar()
            assert stock == Decimal("70.000")  # 50 + 20, no sale
            cnt = s.execute(text("SELECT COUNT(*) FROM sales WHERE fuel_type_id=:id"), {"id": fid}).scalar()
            assert cnt == 0

    def test_many_sales_with_interleaved_refill_never_exceeds_total_available(self, app):
        """
        Start stock=100. Spawn 6 x 25L sale attempts (total demand=150) plus a +30L refill.
        Regardless of interleaving, total sold <= 130 and final stock = 100 + 30 - sold.
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "Interleave", Decimal("95.000"), Decimal("100.000"))
            fid = ft["id"]

        q = Queue()
        threads = []
        # 6 sale attempts of 25L each
        for i in range(6):
            # stagger some starts
            delay = 0.00 if i % 2 == 0 else 0.01
            threads.append(threading.Thread(target=self._sale_worker, args=(sf, fid, "25.000", q, delay)))
        # one refill of +30
        threads.append(threading.Thread(target=self._refill_worker, args=(sf, fid, "30.000", q, 0.005)))

        for t in threads: t.start()
        for t in threads: t.join()

        # Check final invariants
        with session_scope(sf) as s:
            sold = s.execute(text("SELECT COALESCE(SUM(litres),0) FROM sales WHERE fuel_type_id=:id"), {"id": fid}).scalar()
            stock = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fid}).scalar()

            # Never sell more than initial + refill = 130
            assert sold <= Decimal("130.000")
            # Conservation: final stock = 100 + 30 - sold
            assert stock == Decimal("130.000") - sold
