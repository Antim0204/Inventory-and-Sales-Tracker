class TestNotFoundAndConflicts:
    def test_refill_unknown_fuel_type(self, client):
        r = client.post("/inventory/refill", json={"fuel_type_id": 9999, "litres": "10.000"})
        assert r.status_code == 404

    def test_oversell_conflict(self, client):
        r = client.post("/fuel-types", json={"name": "Diesel", "price_per_litre": "90.000", "initial_stock_litres": "5.000"})
        fid = r.get_json()["id"]
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "100.000"})
        assert r.status_code in (400, 409)  # depending on how you mapped it
