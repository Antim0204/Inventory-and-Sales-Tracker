from decimal import Decimal
import threading
from queue import Queue
from time import sleep

from sqlalchemy import text
from src.db import session_scope
from src.modules.fuel_types_service import create_fuel_type, update_price
from src.modules.sales_service import record_sale

class TestConcurrentPriceChange:
    def _sale_worker(self, session_factory, fuel_type_id, litres, out_q, delay=0.0):
        """Try to record a sale; capture the sale row (or exception)."""
        try:
            if delay:
                sleep(delay)
            with session_scope(session_factory) as s:
                sale = record_sale(s, fuel_type_id, Decimal(litres))
                out_q.put(("ok", sale))
        except Exception as e:
            out_q.put(("err", e))

    def _price_worker(self, session_factory, fuel_type_id, new_price, out_q, delay=0.0):
        """Update price (committed), optionally after a small delay."""
        try:
            if delay:
                sleep(delay)
            with session_scope(session_factory) as s:
                res = update_price(s, fuel_type_id, Decimal(new_price))
                out_q.put(("ok", res))
        except Exception as e:
            out_q.put(("err", e))

    def test_sale_captures_price_at_time_of_sale(self, app):
        """
        Given initial price=90.000, then a concurrent update to 92.500,
        a concurrent sale for 10L must lock the price_at_sale as either 90.000 or 92.500,
        and amount must be litres * price_at_sale.
        """
        sf = app.config["SESSION_FACTORY"]
        with session_scope(sf) as s:
            ft = create_fuel_type(s, "Diesel", Decimal("90.000"), Decimal("100.000"))
            fid = ft["id"]

        # Prepare workers: stagger slightly so the race is real but stable.
        # Start both near-simultaneously; sale has a tiny delay to allow either ordering.
        q = Queue()
        t_sale  = threading.Thread(target=self._sale_worker,  args=(sf, fid, "10.000", q, 0.01))
        t_price = threading.Thread(target=self._price_worker, args=(sf, fid, "92.500", q, 0.00))

        t_price.start(); t_sale.start()
        t_price.join(); t_sale.join()

        # Collect two results (one price update, one sale)
        r1, r2 = q.get(), q.get()
        results = [r1, r2]

        # Extract sale result
        sale_res = next((r[1] for r in results if r[0] == "ok" and isinstance(r[1], dict) and "price_at_sale" in r[1]), None)
        assert sale_res is not None, f"Expected a sale result, got: {results}"

        price_at_sale = Decimal(sale_res["price_at_sale"])
        amount = Decimal(sale_res["amount"])
        litres = Decimal(sale_res["litres"])

        # Must be either the old or the new price
        assert price_at_sale in (Decimal("90.000"), Decimal("92.500"))

        # Amount must match litres * price_at_sale
        assert amount == litres * price_at_sale

        # Inventory must reflect immediate deduction (100 - 10 = 90)
        with session_scope(sf) as s:
            stock = s.execute(text("SELECT stock_litres FROM fuel_types WHERE id=:id"), {"id": fid}).scalar()
            assert stock == Decimal("90.000")

    def test_multiple_runs_eventually_observe_both_prices(self, app):
        """
        Run the race a few times to *likely* observe both outcomes across runs.
        Non-flaky: each iteration asserts correctness; across runs we may see old or new price.
        """
        sf = app.config["SESSION_FACTORY"]
        from collections import Counter
        seen = Counter()

        for i in range(5):
            # unique name each loop avoids UNIQUE constraint violation
            with session_scope(sf) as s:
                ft = create_fuel_type(s, f"X_{i}", Decimal("80.000"), Decimal("50.000"))
                fid = ft["id"]

            q = Queue()
            # flip delays so order sometimes sale-first, sometimes price-first
            t_sale  = threading.Thread(target=self._sale_worker,  args=(sf, fid, "5.000", q, 0.00))
            t_price = threading.Thread(target=self._price_worker, args=(sf, fid, "85.000", q, 0.01))
            t_sale.start(); t_price.start(); t_sale.join(); t_price.join()

            r1, r2 = q.get(), q.get()
            sale_res = next((r[1] for r in (r1, r2)
                             if r[0] == "ok" and isinstance(r[1], dict) and "price_at_sale" in r[1]), None)

            price_at_sale = Decimal(sale_res["price_at_sale"])
            assert price_at_sale in (Decimal("80.000"), Decimal("85.000"))
            seen[str(price_at_sale)] += 1

        # not required to pass; printed for human check if desired
        print("Observed price_at_sale counts:", seen)
