# Security notes

## Secrets and config
- `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`, and `SERVERS_KEY` come from `.env` only.
- `.env` is gitignored; commit `.env.example` with empty placeholders.
- Never store plaintext admin passwords — only Werkzeug hashes.
- SSH passwords in `servers.json` are Fernet-encrypted using key material from `SERVERS_KEY`. Keep the file mode `0600` when possible (`ServerStore` attempts this).

## Authentication
- Failed logins always show the same message (no user enumeration).
- Username compared with `hmac.compare_digest`; password via `check_password_hash`.
- Empty/oversized inputs rejected (username ≤ 128, password ≤ 512).
- Session regenerated on login; cleared on logout.
- `SESSION_COOKIE_HTTPONLY`; `SESSION_COOKIE_SECURE` in production; 30-minute idle lifetime.

## CSRF and headers
- Flask-WTF CSRFProtect on state-changing routes (login POST, server CRUD/test).
- HTML forms include `csrf_token`; JS APIs send `X-CSRFToken`.
- Headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, CSP (`default-src 'self'`), HSTS when not in debug.

## Monitoring APIs
- All `/api/stats*` routes require login.
- Process list exposes name/pid/cpu/mem only — not full command lines or env.
- Rate limiting is not enforced in-app yet; put a reverse proxy limit in front for production.
- Stats GET is read-only; CSRF applies to state-changing POSTs/PUTs/DELETEs.

## Remote SSH
- Commands are fixed allowlists in code (`LINUX_COMMANDS` / `WINDOWS_COMMANDS`). User fields never enter the shell string.
- Host key policy prefers system `known_hosts` + `RejectPolicy`, with AutoAdd fallback for lab demos.
- Metadata IP `169.254.169.254` and loopback targets are blocked.
- Residual risk: private LAN targets remain allowed (needed for monitoring). Do not expose this app to the public internet without additional controls.
- Client-facing remote errors are generic (`Unable to collect remote stats`).

## Test connection
- `/api/servers/test` performs a short TCP connect only (timeout ~3s). It does **not** authenticate SSH or run commands.

## Production
- `ProductionConfig`: `DEBUG=False`, secure cookies.
- Do not use `python run.py` in production — use Gunicorn behind HTTPS termination.
- CI runs `pip-audit` and fails on known vulnerable dependencies.

## Checklist
- [x] Secrets only via env / gitignored `.env`
- [x] Password hashes only
- [x] CSRF on mutating forms/APIs
- [x] Security headers
- [x] Auth on stats + server routes
- [x] Encrypted SSH passwords at rest
- [x] Allowlisted remote commands
- [x] CI lint + tests + dependency audit
