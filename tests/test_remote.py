from unittest.mock import MagicMock, patch

from app.services.remote_monitor import LINUX_COMMANDS, RemoteMonitor, is_blocked_target


def test_commands_are_allowlisted_constants():
    # Guarantees we never build shell from user-controlled fields.
    for command in LINUX_COMMANDS.values():
        assert "{}" not in command
        assert "%s" not in command


def test_metadata_ip_blocked():
    assert is_blocked_target("169.254.169.254") is True
    assert is_blocked_target("127.0.0.1") is True


def test_remote_stats_requires_known_server(auth_client):
    response = auth_client.get("/api/stats/missing.example")
    assert response.status_code == 404


def test_remote_stats_uses_store_host_not_injection(auth_client, app):
    auth_client.post(
        "/api/servers",
        json={
            "host": "remote.example",
            "username": "ubuntu",
            "password": "pw",
            "port": 22,
            "os_type": "linux",
            "name": "remote",
        },
    )
    fake_stats = {
        "cpu": {"percent": 0, "count": 1, "frequency": {"current": 0}},
        "memory": {"total": 1, "used": 0, "available": 1, "percent": 0},
        "disk": [],
        "network": {},
        "processes": [],
        "host": "remote.example",
        "os_type": "linux",
    }
    with patch("app.routes.dashboard.RemoteMonitor") as mock_cls:
        mock_cls.return_value.get_all_stats.return_value = fake_stats
        response = auth_client.get("/api/stats/remote.example")
    assert response.status_code == 200
    # Host/username come from store fields, not free-form shell.
    kwargs = mock_cls.call_args.kwargs
    assert kwargs["host"] == "remote.example"
    assert kwargs["username"] == "ubuntu"


def test_remote_monitor_runs_only_allowlisted(monkeypatch):
    monitor = RemoteMonitor("example.com", "u", "p", os_type="linux")
    executed = []

    class FakeClient:
        def exec_command(self, command, timeout=12):
            executed.append(command)
            stdout = MagicMock()
            stdout.read.return_value = b"0"
            stderr = MagicMock()
            stderr.read.return_value = b""
            return MagicMock(), stdout, stderr

        def close(self):
            return None

    monkeypatch.setattr(monitor, "_connect", lambda timeout=8: FakeClient())
    monitor.get_all_stats()
    assert executed
    assert set(executed).issubset(set(LINUX_COMMANDS.values()))
