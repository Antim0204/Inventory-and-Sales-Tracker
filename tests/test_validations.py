class TestValidations:
    def test_create_fuel_type_negative_price(self, client):
        r = client.post("/fuel-types", json={
            "name": "Petrol", "price_per_litre": "-1.000", "initial_stock_litres": "0.000"
        })
        assert r.status_code == 400

    def test_refill_nonpositive_litres(self, client):
        r = client.post("/inventory/refill", json={"fuel_type_id": 123, "litres": "0.000"})
        assert r.status_code == 400

    def test_update_price_negative(self, client):
        # first create
        r = client.post("/fuel-types", json={"name": "Diesel", "price_per_litre": "90.000"})
        fid = r.get_json()["id"]
        # then try bad price
        r = client.patch(f"/fuel-types/{fid}/price", json={"price_per_litre": "-2.000"})
        assert r.status_code == 400
    def test_sale_nonpositive_litres(self, client):
        # First create a valid fuel type
        r = client.post("/fuel-types", json={
            "name": "Diesel", "price_per_litre": "90.000", "initial_stock_litres": "100.000"
        })
        fid = r.get_json()["id"]

        # Try to sell 0 litres -> should trigger ValidationError in record_sale
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "0.000"})
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] == "BAD_REQUEST"
