class TestMetaEndpoints:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.get_json()
        assert body == {"status": "healthy"}

    def test_index_lists_endpoints(self, client):
        r = client.get("/")
        assert r.status_code == 200
        body = r.get_json()
        assert body.get("status") == "ok"
        assert "endpoints" in body and isinstance(body["endpoints"], list)
