import pytest
from flask_session import Session
from werkzeug.security import generate_password_hash

from app import create_app

TEST_USERNAME = "testadmin"
TEST_PASSWORD = "test-password-not-for-prod"
TEST_PASSWORD_HASH = generate_password_hash(TEST_PASSWORD)
TEST_SERVERS_KEY = "test-servers-key-not-for-prod"


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-for-prod")
    monkeypatch.setenv("ADMIN_USERNAME", TEST_USERNAME)
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", TEST_PASSWORD_HASH)
    monkeypatch.setenv("SERVERS_KEY", TEST_SERVERS_KEY)
    monkeypatch.setenv("FLASK_ENV", "development")

    application = create_app("development")
    application.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-not-for-prod",
            "ADMIN_USERNAME": TEST_USERNAME,
            "ADMIN_PASSWORD_HASH": TEST_PASSWORD_HASH,
            "SERVERS_KEY": TEST_SERVERS_KEY,
            "SERVERS_FILE": str(tmp_path / "servers.json"),
            "SESSION_TYPE": "filesystem",
            "SESSION_FILE_DIR": str(tmp_path / "sessions"),
            "SESSION_USE_SIGNER": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    # Re-bind Flask-Session after SESSION_FILE_DIR is known.
    Session(application)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    response = client.post(
        "/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers.get("Location", "")
    return client
