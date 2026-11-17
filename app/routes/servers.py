from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError

from app.security import login_required
from app.services.remote_monitor import tcp_probe
from app.services.server_store import VALID_OS, ServerStore, get_store

servers_bp = Blueprint("servers", __name__)


def _csrf_ok() -> bool:
    if not current_app.config.get("WTF_CSRF_ENABLED", True):
        return True
    token = request.headers.get("X-CSRFToken") or request.form.get("csrf_token")
    try:
        validate_csrf(token)
        return True
    except ValidationError:
        return False


@servers_bp.route("/servers")
@login_required
def index():
    os_type = request.args.get("os_type", "linux")
    if os_type not in VALID_OS:
        os_type = "linux"
    servers = get_store().list_servers(os_type=os_type)
    return render_template("servers.html", os_type=os_type, servers=servers)


@servers_bp.route("/api/servers", methods=["GET"])
@login_required
def list_servers():
    os_type = request.args.get("os_type")
    return jsonify(get_store().list_servers(os_type=os_type))


@servers_bp.route("/api/servers", methods=["POST"])
@login_required
def add_server():
    if not _csrf_ok():
        return jsonify({"error": "Invalid CSRF token"}), 400

    data = request.get_json(silent=True) or {}
    host = (data.get("host") or "").strip()
    username = (data.get("username") or "").strip()
    os_type = (data.get("os_type") or "linux").lower()
    try:
        port = int(data.get("port") or 22)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid port"}), 400

    if not ServerStore.validate_host(host) or not username:
        return jsonify({"error": "Valid host and username are required"}), 400
    if not ServerStore.validate_port(port):
        return jsonify({"error": "Invalid port"}), 400
    if os_type not in VALID_OS:
        return jsonify({"error": "Invalid OS type"}), 400

    server = {
        "host": host,
        "os_type": os_type,
        "username": username,
        "password": data.get("password") or "",
        "port": port,
        "name": (data.get("name") or host).strip()[:128],
    }
    if not get_store().add_server(server):
        return jsonify({"error": "Server already exists"}), 409
    return jsonify({"success": True, "host": host}), 201


@servers_bp.route("/api/servers/<path:host>", methods=["PUT"])
@login_required
def update_server(host):
    if not _csrf_ok():
        return jsonify({"error": "Invalid CSRF token"}), 400
    data = request.get_json(silent=True) or {}
    updates = {}
    if "port" in data:
        try:
            port = int(data["port"])
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid port"}), 400
        if not ServerStore.validate_port(port):
            return jsonify({"error": "Invalid port"}), 400
        updates["port"] = port
    if data.get("password"):
        updates["password"] = data["password"]
    if "name" in data:
        updates["name"] = (data.get("name") or host).strip()[:128]
    if "username" in data:
        updates["username"] = (data.get("username") or "").strip()[:128]
    if not get_store().update_server(host, updates):
        return jsonify({"error": "Server not found"}), 404
    return jsonify({"success": True})


@servers_bp.route("/api/servers/<path:host>", methods=["DELETE"])
@login_required
def delete_server(host):
    if not _csrf_ok():
        return jsonify({"error": "Invalid CSRF token"}), 400
    if not get_store().remove_server(host):
        return jsonify({"error": "Server not found"}), 404
    return jsonify({"success": True})


@servers_bp.route("/api/servers/test", methods=["POST"])
@login_required
def test_connection():
    """Shallow TCP check only — does not authenticate over SSH."""
    if not _csrf_ok():
        return jsonify({"error": "Invalid CSRF token"}), 400
    data = request.get_json(silent=True) or {}
    host = (data.get("host") or "").strip()
    try:
        port = int(data.get("port") or 22)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid port"}), 400
    if not ServerStore.validate_host(host) or not ServerStore.validate_port(port):
        return jsonify({"success": False, "message": "Invalid host or port"}), 400
    ok, message = tcp_probe(host, port)
    return jsonify({"success": ok, "message": message})


@servers_bp.route("/servers/add", methods=["POST"])
@login_required
def add_server_form():
    """HTML form fallback with CSRF field."""
    if not _csrf_ok():
        flash("Invalid CSRF token", "error")
        return redirect(url_for("servers.index"))
    host = (request.form.get("host") or "").strip()
    username = (request.form.get("username") or "").strip()
    os_type = (request.form.get("os_type") or "linux").lower()
    try:
        port = int(request.form.get("port") or 22)
    except ValueError:
        flash("Invalid port", "error")
        return redirect(url_for("servers.index", os_type=os_type))
    if not ServerStore.validate_host(host) or not username or os_type not in VALID_OS:
        flash("Invalid server details", "error")
        return redirect(url_for("servers.index", os_type=os_type))
    ok = get_store().add_server(
        {
            "host": host,
            "username": username,
            "password": request.form.get("password") or "",
            "port": port,
            "os_type": os_type,
            "name": (request.form.get("name") or host).strip()[:128],
        }
    )
    flash("Server added." if ok else "Server already exists.", "success" if ok else "error")
    return redirect(url_for("servers.index", os_type=os_type))
