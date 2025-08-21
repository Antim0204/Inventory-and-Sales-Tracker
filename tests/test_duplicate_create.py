# tests/test_duplicate_create.py

class TestDuplicateCreate:
    def test_duplicate_fuel_type_returns_409(self, client):
        # First create should succeed
        r1 = client.post(
            "/fuel-types",
            json={"name": "Diesel", "price_per_litre": "90.000", "initial_stock_litres": "0.000"},
        )
        assert r1.status_code == 201
        first = r1.get_json()
        assert "id" in first

        # Second create with same name should fail with 409
        r2 = client.post(
            "/fuel-types",
            json={"name": "Diesel", "price_per_litre": "95.000", "initial_stock_litres": "100.000"},
        )
        assert r2.status_code == 409
        body = r2.get_json()
        assert body["error"]["code"] == "CONFLICT"
        assert "already exists" in body["error"]["message"]

        # Sanity: DB should still only contain 1 Diesel fuel type
        r3 = client.get("/fuel-types")
        all_fuels = r3.get_json()
        diesel_fuels = [ft for ft in all_fuels if ft["name"] == "Diesel"]
        assert len(diesel_fuels) == 1
