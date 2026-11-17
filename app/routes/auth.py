from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError

from app.services.auth_service import verify_credentials

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        if current_app.config.get("WTF_CSRF_ENABLED", True):
            try:
                validate_csrf(request.form.get("csrf_token"))
            except ValidationError:
                flash("Invalid CSRF token", "error")
                return redirect(url_for("auth.login"))

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if verify_credentials(username, password):
            session.clear()
            session["logged_in"] = True
            session["username"] = current_app.config.get("ADMIN_USERNAME")
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard.index"))

        flash("Invalid username or password", "error")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
