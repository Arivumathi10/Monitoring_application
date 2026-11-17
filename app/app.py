import os

from flask import Flask
from flask_session import Session

from app.config import config


def create_app(config_name=None):
    """Application factory."""
    app = Flask(__name__)

    name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config.get(name, config["default"]))

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be set in the environment (via .env)."
        )

    Session(app)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
