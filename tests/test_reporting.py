class TestReportingAPI:
    def test_reporting_endpoints(self, client):
        # seed a little data
        r = client.post("/fuel-types", json={"name":"Diesel","price_per_litre":"90.000","initial_stock_litres":"200.000"})
        fid = r.get_json()["id"]
        client.post("/sales", json={"fuel_type_id": fid, "litres":"10.000"})
        client.patch(f"/fuel-types/{fid}/price", json={"price_per_litre":"92.500"})
        client.post("/sales", json={"fuel_type_id": fid, "litres":"5.000"})

        # overview
        r = client.get("/reports/sales/overview")
        assert r.status_code == 200
        assert "total_revenue" in r.get_json()

        # timeseries
        r = client.get("/reports/sales/timeseries?granularity=day")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

        # by fuel type
        r = client.get("/reports/sales/by-fuel-type")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

        # price history
        r = client.get(f"/reports/price/history?fuel_type_id={fid}")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)
   
    def test_reporting_invalid_date_param(self, client):
        # Bad "from" param -> marshmallow ValidationError
        r = client.get("/reports/sales/overview?from=not-a-date")
        assert r.status_code == 400
        assert r.get_json()["error"]["code"] in ("BAD_REQUEST", "VALIDATION_ERROR")

    def test_price_history_missing_fuel_type_id(self, client):
        # Missing required param -> triggers custom ValidationError
        r = client.get("/reports/price/history")
        assert r.status_code == 400
        body = r.get_json()
        assert body["error"]["code"] in ("BAD_REQUEST", "VALIDATION_ERROR")
        assert "fuel_type_id" in body["error"]["message"]
