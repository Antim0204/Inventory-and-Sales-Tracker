from decimal import Decimal

class TestExactStockDepletion:
    def test_sell_exact_remaining_then_fail_next(self, client):
        # Seed 50L at price 90
        r = client.post("/fuel-types", json={"name": "Exact", "price_per_litre": "90.000", "initial_stock_litres": "50.000"})
        assert r.status_code == 201
        fid = r.get_json()["id"]

        # Sell exactly 50L
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "50.000"})
        assert r.status_code == 201

        # Inventory should be 0
        r = client.get("/inventory")
        inv = r.get_json()
        rec = next(x for x in inv if x["fuel_type_id"] == fid)
        assert Decimal(rec["stock_litres"]) == Decimal("0.000")

        # Any further sale should fail with insufficient stock
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "1.000"})
        assert r.status_code in (400, 409)
        body = r.get_json()
        assert body["error"]["code"] in ("INSUFFICIENT_STOCK", "BAD_REQUEST")
