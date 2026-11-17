from functools import wraps

from flask import Blueprint, flash, redirect, render_template, session, url_for

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please sign in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@dashboard_bp.route("/dashboard")
@login_required
def index():
    return render_template("dashboard.html")
