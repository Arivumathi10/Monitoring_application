import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Development helper only. Production: gunicorn 'app:create_app()'
    if not app.config.get("DEBUG"):
        raise SystemExit(
            "Refusing to run the development server when DEBUG is False. Use Gunicorn."
        )
    port = int(os.getenv("PORT", "5013"))
    app.run(debug=True, port=port, use_reloader=False)
