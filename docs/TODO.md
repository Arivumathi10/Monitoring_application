# Implementation TODO

Incremental checklist for AI-assisted development. Complete items **in order**. Each step is intentionally small: one concern, one reviewable change.

**Product goal:** Flask web app for local/remote system monitoring (CPU, memory, disk, network, processes) with admin sign-in and managed SSH targets.

**Rules for every step**
- Keep diffs small and reviewable.
- Do not hardcode secrets; use `.env` / config.
- Update docs in the same step as the code.
- Complete the **Security** and **Docs** checkboxes before marking a step done.

---

## Phase 0 — Project initialization and Basic UI

### 0.1 Repository scaffold
- [x] Create project layout (`app/`, `app/routes/`, `app/services/`, `app/templates/`, `app/static/`, `docs/`, `tests/`)
- [x] Add `.gitignore` (`.venv/`, `.env`, `__pycache__/`, `flask_session/`, `*.pyc`, IDE junk)
- [x] **Security:** Ensure `.env` is gitignored; never commit secrets
- [x] **Docs:** Add short `README.md` with purpose, stack (Python 3.11+, Flask), and folder overview

### 0.2 Dependencies and virtualenv
- [x] Add `app/requirements.txt` with pinned minimums (`flask`, `python-dotenv` only at this stage)
- [x] Document `python -m venv .venv` and `pip install -r app/requirements.txt`
- [x] **Security:** Prefer minimum dependency set; record why each package is needed in README
- [x] **Docs:** Add “Local setup” section to `README.md`

### 0.3 App factory (no features yet)
- [x] Add `app/config.py` with `Config` / Dev / Prod reading from env via `python-dotenv`
- [x] Add `app/app.py` with `create_app()` and `if __name__ == "__main__":` guard
- [x] Add `run.py` entry point
- [x] **Security:** Require `SECRET_KEY` from env; fail fast if missing; `debug` only via Dev config (never hardcode prod debug)
- [x] **Docs:** Document config vars in `.env.example` (`SECRET_KEY=` placeholder only)

### 0.4 Basic UI shell
- [x] Add base Jinja layout (nav placeholder, flash area, CSS link)
- [x] Add home page template + thin blueprint route that renders it
- [x] Add minimal `static/css/style.css` for readable layout
- [x] **Security:** Escape all template output by default (no `|safe` unless justified); no inline user-controlled HTML
- [x] **Docs:** Document routes so far in `docs/architecture.md` (one paragraph + route table)

### 0.5 Phase 0 definition of done
- [x] App starts locally and serves a static home page
- [x] README + `.env.example` + `docs/architecture.md` updated
- [x] Manual smoke: open `/` in browser

---

## Phase 1 — Sign-in functionality and unit tests

### 1.1 Auth config
- [x] Add `ADMIN_USERNAME` and `ADMIN_PASSWORD_HASH` to config / `.env.example`
- [x] Document how to generate a Werkzeug password hash
- [x] **Security:** Store only password **hashes**, never plaintext passwords in `.env` or code
- [x] **Docs:** Add “Authentication” section to README (hash generation command)

### 1.2 Auth service (logic only)
- [x] Add `app/services/auth_service.py` with `verify_credentials(username, password)`
- [x] Keep routes thin — no credential logic in the view
- [x] **Security:** Constant-time username compare; `check_password_hash`; reject empty/oversized inputs; return generic failure (no user enumeration)
- [x] **Docs:** Note threat model for login failures in `docs/security.md`

### 1.3 Sign-in / sign-out routes and UI
- [x] Add auth blueprint: `GET/POST /login`, `GET /logout`
- [x] Add `login.html` form (username + password)
- [x] Flash generic “Invalid username or password” on failure
- [x] **Security:** POST-only credential submission; session regenerated on login; clear session on logout; do not echo password back
- [x] **Docs:** Update route table in `docs/architecture.md`

### 1.4 Session setup
- [x] Enable server-side sessions (`Flask-Session` or equivalent) with filesystem store
- [x] Protect a sample “dashboard” route behind `logged_in` session check
- [x] Redirect unauthenticated users to `/login`
- [x] **Security:** Signed sessions; `SESSION_COOKIE_HTTPONLY`; document `SESSION_COOKIE_SECURE` for HTTPS/prod; short idle lifetime
- [x] **Docs:** Document session settings in `docs/security.md`

### 1.5 Unit tests for sign-in
- [x] Add `tests/` with pytest + Flask test client fixture
- [x] Tests: missing env credentials → reject; wrong password → reject; correct credentials → session set; logout clears session; oversized input → reject
- [x] Add `requirements-dev.txt` (or optional extras) for `pytest`
- [x] **Security:** Tests must not embed real production secrets; use throwaway hashes in fixtures
- [x] **Docs:** Add “Running tests” to README (`pytest`)

### 1.6 Phase 1 definition of done
- [x] Can sign in / sign out through the UI
- [x] Auth unit tests pass locally
- [x] `docs/security.md` covers credentials + sessions

---

## Phase 2 — CI/CD (GitHub Actions)

### 2.1 Lint/format baseline (tiny)
- [ ] Add a minimal lint config (e.g. ruff) or document `python -m compileall`
- [ ] **Security:** Fail CI on obvious secret patterns if a scanner is added later; for now ensure `.env` cannot be committed
- [ ] **Docs:** Document local lint command in README

### 2.2 GitHub Actions — test workflow
- [ ] Add `.github/workflows/ci.yml`: install deps, run pytest on push/PR
- [ ] Use Python 3.11+ matrix (single version is fine initially)
- [ ] Inject dummy `SECRET_KEY` / admin test credentials via workflow `env` (not repository secrets of real prod)
- [ ] **Security:** No real secrets in workflow files; use ephemeral CI env values only
- [ ] **Docs:** Add “CI” section describing when checks run and how to read failures

### 2.3 GitHub Actions — quality gate
- [ ] Extend CI to run lint/compile step before tests
- [ ] Mark workflow required for merges (document the GitHub branch-protection click-path)
- [ ] **Security:** CI must fail if tests fail; do not `continue-on-error` for auth tests
- [ ] **Docs:** Update README with badge or link to Actions (optional)

### 2.4 Phase 2 definition of done
- [ ] Opening a PR runs CI; auth tests must pass to go green

---

## Phase 3 — Local host monitoring (read-only)

### 3.1 Monitor interface
- [ ] Add `base_monitor.py` abstract interface (stats shape: CPU, memory, disk, network, processes)
- [ ] **Security:** Define which fields are safe to expose in the UI (no env vars, no file contents)
- [ ] **Docs:** Document stats JSON schema in `docs/architecture.md`

### 3.2 Local collector
- [ ] Add local monitor service using `psutil`
- [ ] Wire `/api/stats` (auth-required) returning `jsonify(...)`
- [ ] **Security:** Require login for all stats APIs; rate-limit note in docs; avoid leaking full process command lines if sensitive
- [ ] **Docs:** Example API response in docs

### 3.3 Dashboard UI
- [ ] Dashboard page that polls `/api/stats`
- [ ] Minimal JS fetch + render (keep JS small)
- [ ] **Security:** Credentials never stored in JS; rely on session cookie; CSRF strategy documented for state-changing routes (stats GET is read-only)
- [ ] **Docs:** Screenshot or short “using the dashboard” blurb in README

### 3.4 Tests
- [ ] Unit test: unauthenticated `/api/stats` → redirect/401
- [ ] Unit test: authenticated client receives expected keys (mock psutil if needed)
- [ ] **Security:** Assert no password/hash fields appear in JSON
- [ ] **Docs:** Note test coverage for monitoring APIs

---

## Phase 4 — Server inventory (CRUD, no remote exec yet)

### 4.1 Encrypted server store
- [ ] Add `server_store.py` persisting to local JSON (or similar)
- [ ] Encrypt stored SSH passwords at rest (e.g. Fernet) using a key derived/configured from env
- [ ] **Security:** Never log passwords; encrypt at rest; key only in env; file permissions guidance
- [ ] **Docs:** Document `SERVERS_KEY` / encryption in `.env.example` and `docs/security.md`

### 4.2 Servers UI + API
- [ ] List / add / edit / delete server forms (host, user, port, OS type)
- [ ] Thin `servers` blueprint; logic in service layer
- [ ] **Security:** Auth required for all server routes; validate host/port input; do not reflect unsanitized host into HTML unsafely
- [ ] **Docs:** Update architecture with servers module

### 4.3 Connection test stub
- [ ] Add “test connection” endpoint that validates input only (or shallow TCP check) before full SSH
- [ ] **Security:** Timeouts; no unbounded connection attempts; do not return raw exception strings to clients
- [ ] **Docs:** Document what “test connection” does and does not do

### 4.4 Tests + docs
- [ ] Unit tests for store encrypt/decrypt round-trip and CRUD authz
- [ ] **Security:** Tests use ephemeral keys; temp files cleaned up
- [ ] **Docs:** Operator guide: adding a server

---

## Phase 5 — Remote monitoring over SSH

### 5.1 Remote monitor service
- [ ] Add `remote_monitor.py` using Paramiko with strict timeouts
- [ ] OS-specific command sets (Linux shell / Windows PowerShell) behind clear allowlists
- [ ] **Security:** Command allowlist only (no user-supplied shell strings); host key policy documented (prefer known_hosts); reject SSRF-prone targets where practical (metadata IPs) and document residual risk
- [ ] **Docs:** Threat notes for SSH remote exec in `docs/security.md`

### 5.2 Remote stats API + monitor page
- [ ] `/api/stats/<host>` and monitor template for a selected server
- [ ] **Security:** Auth required; authorize that `<host>` exists in the user’s server store; generic errors to client
- [ ] **Docs:** Update API table

### 5.3 Tests
- [ ] Mock SSH layer; test allowlist and auth wrappers
- [ ] **Security:** Ensure tests prove arbitrary commands cannot be injected via host name/fields
- [ ] **Docs:** How to run remote-monitor tests offline (mocks)

---

## Phase 6 — Hardening and production readiness

### 6.1 Production config
- [ ] ProductionConfig: `DEBUG=False`; secure cookie flags; document Gunicorn invocation
- [ ] Remove or gate any `app.run(debug=True)` for prod paths
- [ ] **Security:** Confirm debug debugger cannot be enabled in prod
- [ ] **Docs:** “Deploying” section (Gunicorn, env vars, HTTPS termination)

### 6.2 Security headers and CSRF
- [ ] Add basic security headers (or Flask-Talisman-style) for HTML routes
- [ ] CSRF protection on state-changing forms (login, server CRUD)
- [ ] **Security:** Verify login + servers POST reject missing/invalid CSRF tokens
- [ ] **Docs:** Update `docs/security.md` checklist

### 6.3 CI hardening
- [ ] Add dependency audit step (e.g. `pip-audit`) to GitHub Actions
- [ ] Optional: secret scanning / `gitleaks` in CI
- [ ] **Security:** CI fails on known vulnerable deps (document exceptions)
- [ ] **Docs:** Describe audit job in README CI section

### 6.4 Final documentation pass
- [ ] README: quickstart, auth, dashboard, servers, remote monitor, CI, deploy
- [ ] `docs/architecture.md` matches final layout
- [ ] `docs/security.md` complete checklist
- [ ] Mark completed items in this file as you finish them

---

## Suggested AI-assisted batching

Work **one checkbox group** (e.g. `1.2` or `2.2`) per agent session. Do not combine Phase 5 SSH work with Phase 1 auth in the same change.

| Order | Focus |
|------:|-------|
| 1 | Phase 0 — init + basic UI |
| 2 | Phase 1 — sign-in + unit tests |
| 3 | Phase 2 — GitHub Actions CI |
| 4 | Phase 3 — local monitoring |
| 5 | Phase 4 — server inventory |
| 6 | Phase 5 — remote SSH monitoring |
| 7 | Phase 6 — hardening |

---

## Progress log

| Date | Step | Notes |
|------|------|-------|
| 2026-11-17 | Phase 0–1 | Scaffold, auth, sessions, pytest; local `.env` uses admin/admin123 (dev only) |
