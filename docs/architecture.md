# Architecture

Flask app factory (`create_app`) loads config from environment variables, enables signed filesystem sessions + CSRF, attaches security headers, and registers thin blueprints. Business logic lives under `app/services/`.

## Layout

```
app/
  app.py                 # create_app factory
  config.py              # Dev / Prod config
  security.py            # login_required + security headers
  routes/                # main, auth, dashboard, servers
  services/              # auth, local/remote monitors, server_store
  templates/             # Jinja2 HTML
  static/css|js          # Styles and small polling scripts
tests/                   # pytest (auth, monitor, servers, remote, csrf)
.github/workflows/ci.yml # lint, tests, pip-audit
run.py                   # Local entry point (not for production)
```

## Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Public home |
| GET/POST | `/login` | No | Sign-in (CSRF on POST) |
| GET | `/logout` | Session clear | Sign out |
| GET | `/dashboard` | Yes | Inventory overview |
| GET | `/monitor` | Yes | Local monitor UI |
| GET | `/monitor/<host>` | Yes | Remote monitor UI |
| GET | `/api/stats` | Yes | Local stats JSON |
| GET | `/api/stats/<host>` | Yes | Remote stats JSON (host must exist in store) |
| GET | `/servers` | Yes | Server inventory UI |
| GET/POST | `/api/servers` | Yes | List / add servers (CSRF on POST) |
| PUT/DELETE | `/api/servers/<host>` | Yes | Update / delete (CSRF) |
| POST | `/api/servers/test` | Yes | TCP probe only (CSRF) |

## Stats JSON schema (safe fields)

```json
{
  "cpu": {"percent": 0, "count": 0, "frequency": {"current": 0}},
  "memory": {"total": 0, "used": 0, "available": 0, "percent": 0},
  "disk": [{"device": "", "mountpoint": "", "total": 0, "used": 0, "free": 0, "percent": 0}],
  "network": {"bytes_sent": 0, "bytes_recv": 0},
  "processes": [{"pid": 0, "name": "", "cpu_percent": 0, "memory_percent": 0, "status": ""}],
  "host": "localhost"
}
```

Never included: env vars, file contents, credentials, password hashes.

## Example `/api/stats` response

Authenticated `GET /api/stats` returns the schema above for the local host. Unauthenticated callers are redirected to `/login`.
