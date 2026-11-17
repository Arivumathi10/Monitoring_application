from app.services.server_store import ServerStore


def test_store_encrypt_roundtrip(tmp_path):
    path = tmp_path / "servers.json"
    store = ServerStore(storage_path=str(path), key_material="ephemeral-test-key")
    assert store.add_server(
        {
            "host": "example.test",
            "username": "ubuntu",
            "password": "s3cret",
            "port": 22,
            "os_type": "linux",
            "name": "demo",
        }
    )
    raw = path.read_text()
    assert "s3cret" not in raw
    got = store.get_server("example.test", with_credentials=True)
    assert got["password"] == "s3cret"
    listed = store.list_servers()
    assert listed[0]["host"] == "example.test"
    assert "password" not in listed[0]


def test_servers_require_auth(client):
    response = client.get("/servers", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_server_crud(auth_client):
    created = auth_client.post(
        "/api/servers",
        json={
            "host": "box.example",
            "username": "ops",
            "password": "pw",
            "port": 22,
            "os_type": "linux",
            "name": "box",
        },
    )
    assert created.status_code == 201
    listed = auth_client.get("/api/servers")
    assert listed.status_code == 200
    assert any(s["host"] == "box.example" for s in listed.get_json())
    deleted = auth_client.delete("/api/servers/box.example")
    assert deleted.status_code == 200


def test_test_connection_invalid_host(auth_client):
    response = auth_client.post(
        "/api/servers/test",
        json={"host": "bad host!!", "port": 22},
    )
    assert response.status_code == 400
