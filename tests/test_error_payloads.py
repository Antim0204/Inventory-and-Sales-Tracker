import pytest

class TestErrorPayloads:
    def _assert_error_shape(self, r, expected_status, expected_code=None):
        assert r.status_code == expected_status
        body = r.get_json()
        assert isinstance(body, dict) and "error" in body
        err = body["error"]
        assert "code" in err and "message" in err
        if expected_code:
            assert err["code"] == expected_code

    def test_404_not_found_route(self, client):
        r = client.get("/does-not-exist")
        # Our global HTTPException handler maps to code "NOT_FOUND"
        self._assert_error_shape(r, 404, "NOT_FOUND")

    def test_400_bad_request_validation(self, client):
        # litres <= 0 should trigger 400 BAD_REQUEST from validations
        r = client.post("/sales", json={"fuel_type_id": 9999, "litres": "0.000"})
        self._assert_error_shape(r, 400, "BAD_REQUEST")

    def test_409_conflict_insufficient_stock(self, client):
        # Create fuel type with tiny stock, then oversell
        r = client.post("/fuel-types", json={"name": "ErrDiesel", "price_per_litre": "90.000", "initial_stock_litres": "1.000"})
        fid = r.get_json()["id"]
        r = client.post("/sales", json={"fuel_type_id": fid, "litres": "5.000"})
        # app may use 409 per our InsufficientStockError mapping
        self._assert_error_shape(r, 409, "INSUFFICIENT_STOCK")

    def test_500_internal_error_with_mock(self, client, mocker):
        # Patch the *imported* symbol in the view module
        mocked = mocker.patch("src.apis.sales.record_sale", side_effect=Exception("boom"))
        r = client.post("/sales", json={"fuel_type_id": 1, "litres": "1.000"})
        self._assert_error_shape(r, 500, "INTERNAL_ERROR")
        assert mocked.called
