# Architecture

Flask app factory (`create_app`) loads config from environment variables, enables signed filesystem sessions, and registers thin blueprints. Credential checks live in `app/services/auth_service.py`.

## Layout

```
app/
  app.py              # create_app factory
  config.py           # Dev / Prod config
  routes/             # Blueprints (main, auth, dashboard)
  services/           # Business logic (auth_service)
  templates/          # Jinja2 HTML
  static/css/         # Styles
tests/                # pytest
run.py                # Local entry point
```

## Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | Public home page |
| GET/POST | `/login` | No | Sign-in form / credential submit |
| GET | `/logout` | Session clear | Sign out |
| GET | `/dashboard` | Yes | Protected sample page |
