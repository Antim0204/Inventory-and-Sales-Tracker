from decimal import Decimal

class TestPriceLocking:
    def test_sale_uses_current_price_at_time_of_sale(self, client):
        # create @ 90
        r = client.post("/fuel-types", json={"name":"Diesel","price_per_litre":"90.000","initial_stock_litres":"100.000"})
        fid = r.get_json()["id"]

        # sale #1 at 90
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "10.000"})
        assert r.status_code == 201
        assert Decimal(r.get_json()["price_at_sale"]) == Decimal("90.000")

        # update to 92.5
        r = client.patch(f"/fuel-types/{fid}/price", json={"price_per_litre":"92.500"})
        assert r.status_code == 200

        # sale #2 at 92.5
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "10.000"})
        assert Decimal(r.get_json()["price_at_sale"]) == Decimal("92.500")
