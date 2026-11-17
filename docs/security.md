# Security notes (Phase 0–1)

## Secrets and config
- `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD_HASH` come from `.env` only.
- `.env` is gitignored; commit `.env.example` with empty placeholders.
- Never store plaintext passwords — only Werkzeug password hashes.

## Authentication threat model
- Failed logins always show the same message: “Invalid username or password” (no user enumeration).
- Username compared with `hmac.compare_digest` (constant-time).
- Password verified with `check_password_hash` (salted scrypt/pbkdf2).
- Empty and oversized inputs are rejected before hashing (DoS bound: username ≤ 128, password ≤ 512).
- Unconfigured credentials (`ADMIN_*` missing) cause every login to fail closed.

## Sessions
- Flask-Session filesystem store with signed cookies (`SESSION_USE_SIGNER`).
- `SESSION_COOKIE_HTTPONLY=True` (not readable from JS).
- `SESSION_COOKIE_SECURE=True` in production (HTTPS only).
- Idle lifetime: 30 minutes (`PERMANENT_SESSION_LIFETIME`).
- On successful login the session is cleared then re-created (fixation mitigation).
- Logout calls `session.clear()`.

## Templates
- Jinja auto-escapes output; do not use `|safe` for user-controlled data.
- Password fields are never echoed back into the page.
