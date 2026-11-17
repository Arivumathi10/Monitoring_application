from werkzeug.security import generate_password_hash

from tests.conftest import TEST_PASSWORD, TEST_USERNAME


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign in" in response.data


def test_wrong_password_rejected(client):
    response = client.post(
        "/login",
        data={"username": TEST_USERNAME, "password": "wrong-password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    with client.session_transaction() as sess:
        assert not sess.get("logged_in")


def test_correct_credentials_set_session(client):
    response = client.post(
        "/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("logged_in") is True
        assert sess.get("username") == TEST_USERNAME


def test_logout_clears_session(client):
    client.post(
        "/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert not sess.get("logged_in")
        assert "username" not in sess


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_oversized_input_rejected(client):
    response = client.post(
        "/login",
        data={
            "username": "a" * 200,
            "password": "b" * 600,
        },
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data
    with client.session_transaction() as sess:
        assert not sess.get("logged_in")


def test_missing_env_credentials_reject(app, client, monkeypatch):
    app.config["ADMIN_USERNAME"] = None
    app.config["ADMIN_PASSWORD_HASH"] = None
    response = client.post(
        "/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data
    with client.session_transaction() as sess:
        assert not sess.get("logged_in")


def test_empty_credentials_rejected(client):
    response = client.post(
        "/login",
        data={"username": "", "password": ""},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data


def test_verify_credentials_unit(app):
    from app.services.auth_service import verify_credentials

    with app.app_context():
        assert verify_credentials(TEST_USERNAME, TEST_PASSWORD) is True
        assert verify_credentials(TEST_USERNAME, "nope") is False
        assert verify_credentials("", TEST_PASSWORD) is False
        assert verify_credentials(TEST_USERNAME, "x" * 600) is False
        # Ensure plaintext is never compared; wrong hash type fails safely.
        app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("other")
        assert verify_credentials(TEST_USERNAME, TEST_PASSWORD) is False
