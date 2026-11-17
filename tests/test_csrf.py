from tests.conftest import TEST_USERNAME


def test_login_form_includes_csrf_field(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'name="csrf_token"' in response.data


def test_login_rejects_missing_csrf(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    response = client.post(
        "/login",
        data={"username": "x", "password": "y"},
    )
    assert response.status_code == 400


def test_servers_post_rejects_missing_csrf(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["username"] = TEST_USERNAME
    response = client.post(
        "/servers/add",
        data={
            "host": "x.example",
            "username": "u",
            "password": "p",
            "port": "22",
            "os_type": "linux",
        },
    )
    assert response.status_code == 400
