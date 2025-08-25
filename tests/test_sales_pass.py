from decimal import Decimal

class TestSalesPass:
    def test_create_refill_sell_flow(self, client):
        # Create fuel type
        r = client.post("/fuel-types", json={
            "name": "Diesel", "price_per_litre": "90.000", "initial_stock_litres": "500.000"
        })
        assert r.status_code == 201
        fuel = r.get_json(); fuel_id = fuel["id"]

        # Refill
        r = client.post("/inventory/refill", json={"fuel_type_id": fuel_id, "litres": "100.000"})
        assert r.status_code == 200
        assert Decimal(r.get_json()["new_stock_litres"]) == Decimal("600.000")

        # Sell 50L
        r = client.post("/sales", json={"fuel_type_id": fuel_id, "litres": "50.000"})
        assert r.status_code == 201
        sale = r.get_json()
        assert Decimal(sale["price_at_sale"]) == Decimal("90.000")
        assert Decimal(sale["amount"]) == Decimal("4500.00")

        # Inventory decreased
        r = client.get("/inventory")
        inv = r.get_json()
        assert Decimal(inv[0]["stock_litres"]) == Decimal("550.000")

    def test_list_sales_with_filters(self, client):
        # Create & sell
        r = client.post("/fuel-types", json={
            "name": "Petrol", "price_per_litre": "100.000", "initial_stock_litres": "200.000"
        })
        fid = r.get_json()["id"]
        client.post("/sales", json={"fuel_type_id": fid, "litres": "10.000"})

        # List without filters
        r = client.get("/sales")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

        # List with fuel_type_id filter
        r = client.get(f"/sales?fuel_type_id={fid}")
        assert r.status_code == 200
        assert all(s["fuel_type_id"] == fid for s in r.get_json())
        

