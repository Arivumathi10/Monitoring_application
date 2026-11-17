# System Monitor

Flask web app for local/remote system monitoring with secure admin sign-in.

**Stack:** Python 3.11+, Flask, python-dotenv, Flask-Session

## Folder overview

| Path | Purpose |
|------|---------|
| `app/` | Application package (factory, config, routes, services, templates) |
| `tests/` | pytest unit tests |
| `docs/` | Architecture, security, TODO |
| `run.py` | Local entry point |

## Dependencies (why each package)

| Package | Why |
|---------|-----|
| `flask` | Web framework |
| `python-dotenv` | Load secrets from `.env` (never hardcode) |
| `Flask-Session` | Server-side signed sessions |
| `pytest` (dev) | Unit tests |

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env: set SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD_HASH
python run.py
# Optional: PORT=5013 python run.py  (default PORT is 5013)
```

Open http://127.0.0.1:5013/

## Authentication

Generate a password hash (store only the hash in `.env`):

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Default local demo credentials (from `.env` you create): username `admin` / password you hashed. The checked-in local `.env` (gitignored) uses `admin` / `admin123` for development only.

## Running tests

```bash
source .venv/bin/activate
pytest -q
```

Tests use throwaway hashes in fixtures — not production secrets.

## Routes so far

See [docs/architecture.md](docs/architecture.md). Security details: [docs/security.md](docs/security.md).
