from unittest.mock import patch


def test_stats_requires_login(client):
    response = client.get("/api/stats", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_stats_authenticated_shape(auth_client):
    fake = {
        "cpu": {"percent": 1.0, "count": 2, "frequency": {"current": 0}},
        "memory": {"total": 100, "used": 40, "available": 60, "percent": 40},
        "disk": [],
        "network": {"bytes_sent": 1, "bytes_recv": 2},
        "processes": [{"pid": 1, "name": "init", "cpu_percent": 0, "memory_percent": 0}],
    }
    with patch("app.routes.dashboard.get_local_monitor") as mock_get:
        mock_get.return_value.get_all_stats.return_value = fake
        response = auth_client.get("/api/stats")
    assert response.status_code == 200
    data = response.get_json()
    for key in ("cpu", "memory", "disk", "network", "processes"):
        assert key in data
    blob = response.get_data(as_text=True).lower()
    assert "password" not in blob
    assert "password_hash" not in blob
    assert "admin_password" not in blob
