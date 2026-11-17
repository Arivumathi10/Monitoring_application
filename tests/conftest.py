import pytest
from werkzeug.security import generate_password_hash

from app import create_app


# Throwaway credentials for tests only — never production secrets.
TEST_USERNAME = "testadmin"
TEST_PASSWORD = "test-password-not-for-prod"
TEST_PASSWORD_HASH = generate_password_hash(TEST_PASSWORD)


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-not-for-prod")
    monkeypatch.setenv("ADMIN_USERNAME", TEST_USERNAME)
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", TEST_PASSWORD_HASH)
    monkeypatch.setenv("FLASK_ENV", "development")

    application = create_app("development")
    application.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-not-for-prod",
            "ADMIN_USERNAME": TEST_USERNAME,
            "ADMIN_PASSWORD_HASH": TEST_PASSWORD_HASH,
            "SESSION_TYPE": "filesystem",
            "SESSION_FILE_DIR": str(tmp_path / "sessions"),
        }
    )
    return application


@pytest.fixture
def client(app):
    return app.test_client()
