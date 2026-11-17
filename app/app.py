import os

from flask import Flask
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from app.config import config
from app.security import register_security_headers

csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory."""
    app = Flask(__name__)

    name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config.get(name, config["default"]))

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in the environment (via .env).")

    # Disable interactive debugger even if someone forces debug flags.
    if name == "production":
        app.config["DEBUG"] = False
        app.debug = False

    Session(app)
    csrf.init_app(app)
    register_security_headers(app)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.main import main_bp
    from app.routes.servers import servers_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(servers_bp)

    return app


if __name__ == "__main__":
    # Dev-only entry. Production should use Gunicorn (see README).
    application = create_app()
    if application.config.get("DEBUG"):
        application.run(debug=True, port=int(os.getenv("PORT", "5013")))
    else:
        raise RuntimeError("Refuse to run built-in server when DEBUG is false; use Gunicorn.")
