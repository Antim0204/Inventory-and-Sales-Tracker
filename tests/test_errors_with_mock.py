import pytest

class TestInternalErrors:
    def test_sales_internal_error(self, client, mocker):
        # mock the sales_service.record_sale to raise Exception
        mocked = mocker.patch("src.apis.sales.record_sale", side_effect=Exception("boom"))
        r = client.post("/sales", json={"fuel_type_id": 1, "litres": "1.000"})
        assert r.status_code == 500
        body = r.get_json()
        assert body["error"]["code"] == "INTERNAL_ERROR"
        assert mocked.called
