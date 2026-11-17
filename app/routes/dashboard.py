from flask import Blueprint, jsonify, render_template

from app.security import login_required
from app.services.local_monitor import get_local_monitor
from app.services.remote_monitor import RemoteMonitor
from app.services.server_store import get_store

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    servers = get_store().list_servers()
    return render_template("dashboard.html", servers=servers)


@dashboard_bp.route("/monitor")
@dashboard_bp.route("/monitor/<path:host>")
@login_required
def monitor(host="localhost"):
    if host != "localhost":
        server = get_store().get_server(host)
        if not server:
            return render_template("monitor.html", host=host, missing=True), 404
        os_type = server.get("os_type", "linux")
    else:
        os_type = "local"
    return render_template("monitor.html", host=host, os_type=os_type, missing=False)


@dashboard_bp.route("/api/stats")
@login_required
def local_stats():
    monitor = get_local_monitor()
    payload = monitor.get_all_stats()
    payload["host"] = "localhost"
    return jsonify(payload)


@dashboard_bp.route("/api/stats/<path:host>")
@login_required
def remote_stats(host):
    server = get_store().get_server(host, with_credentials=True)
    if not server:
        return jsonify({"error": "Server not found"}), 404
    try:
        monitor = RemoteMonitor(
            host=server["host"],
            username=server["username"],
            password=server.get("password") or "",
            port=int(server.get("port") or 22),
            os_type=server.get("os_type") or "linux",
        )
        return jsonify(monitor.get_all_stats())
    except Exception:
        return jsonify({"error": "Unable to collect remote stats"}), 502
