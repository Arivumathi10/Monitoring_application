# System Monitor

Flask web app for local/remote system monitoring with secure admin sign-in and encrypted SSH server inventory.

**Stack:** Python 3.11+, Flask, python-dotenv, Flask-Session, psutil, cryptography, Paramiko, Flask-WTF, Gunicorn

[![CI](https://github.com/Arivumathi10/Monitoring_application/actions/workflows/ci.yml/badge.svg)](https://github.com/Arivumathi10/Monitoring_application/actions/workflows/ci.yml)

## Folder overview

| Path | Purpose |
|------|---------|
| `app/` | Application package |
| `tests/` | pytest unit tests |
| `docs/` | Architecture, security, TODO |
| `.github/workflows/ci.yml` | GitHub Actions CI |
| `run.py` | Local entry point only |

## Dependencies (why each package)

| Package | Why |
|---------|-----|
| `flask` | Web framework |
| `python-dotenv` | Load secrets from `.env` |
| `Flask-Session` | Server-side signed sessions |
| `psutil` | Local host metrics |
| `cryptography` | Fernet encryption for SSH passwords at rest |
| `paramiko` | Remote SSH monitoring |
| `Flask-WTF` | CSRF protection |
| `gunicorn` | Production WSGI server |
| `pytest` / `ruff` / `pip-audit` (dev) | Tests, lint, dependency audit |

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env: SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD_HASH, SERVERS_KEY
python run.py
```

Open http://127.0.0.1:5013/

### Lint locally

```bash
python -m compileall -q app tests run.py
ruff check app tests run.py
```

## Authentication

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
python -c "import secrets; print(secrets.token_hex(32))"
python -c "import secrets; print(secrets.token_urlsafe(32))"  # SERVERS_KEY
```

Dev convenience (gitignored `.env`): `admin` / `admin123`.

## Using the dashboard

1. Sign in.
2. Open **Dashboard** → **Monitor this host** to poll local `/api/stats` every 5s.
3. Open **Servers** to add SSH targets (passwords encrypted at rest).
4. Use **Test TCP** for a shallow port check (not SSH auth).
5. Click **Monitor** on a server to poll `/api/stats/<host>`.

## Running tests

```bash
pytest -q
```

Tests use throwaway hashes/keys and mock SSH. Remote-monitor tests run fully offline.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR to `main`:

1. `compileall` + `ruff`
2. `pytest`
3. `pip-audit`

Failures are visible under the repo **Actions** tab. Auth/monitor tests must pass — jobs do not use `continue-on-error`.

### Branch protection (make CI required)

1. GitHub repo → **Settings** → **Branches** → **Add rule** for `main`
2. Enable **Require a pull request before merging** (optional but recommended)
3. Enable **Require status checks to pass** → select the **CI / test** check
4. Save

## Deploying (production)

```bash
export FLASK_ENV=production
export SECRET_KEY=... ADMIN_USERNAME=... ADMIN_PASSWORD_HASH=... SERVERS_KEY=...
gunicorn -b 0.0.0.0:8000 "run:app"
```

Terminate TLS at a reverse proxy (nginx/Caddy). Do not run `python run.py` in production (`DEBUG` paths are gated).

## Docs

- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [TODO](docs/TODO.md)
