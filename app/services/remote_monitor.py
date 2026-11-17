"""Remote host monitoring over SSH with allowlisted commands only."""
from __future__ import annotations

import ipaddress
import socket

import paramiko

# Fixed command sets — never interpolate user input into these strings.
LINUX_COMMANDS = {
    "cpu": "grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}'",
    "cpu_count": "nproc",
    "memory": "free -b | awk '/Mem:/{print $2,$3,$7}'",
    "disk": "df -B1 -P 2>/dev/null | awk 'NR>1 {print $1,$6,$2,$3,$4}'",
    "network": "cat /proc/net/dev",
    "processes": "ps -eo pid,comm,pcpu,pmem,stat --sort=-pcpu | head -n 11",
}

WINDOWS_COMMANDS = {
    "cpu": (
        "powershell -NoProfile -Command "
        "\"(Get-CimInstance Win32_Processor).LoadPercentage\""
    ),
    "cpu_count": (
        "powershell -NoProfile -Command "
        "\"(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors\""
    ),
    "memory": (
        "powershell -NoProfile -Command "
        "\"$o=Get-CimInstance Win32_OperatingSystem; "
        "Write-Output ($o.TotalVisibleMemorySize*1024); "
        "Write-Output (($o.TotalVisibleMemorySize-$o.FreePhysicalMemory)*1024); "
        "Write-Output ($o.FreePhysicalMemory*1024)\""
    ),
    "processes": (
        "powershell -NoProfile -Command "
        "\"Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 "
        "Id,ProcessName | Format-Table -HideTableHeaders\""
    ),
}

# Block cloud metadata and obvious local/self targets. Private LAN hosts remain
# allowed for lab monitoring; residual SSRF risk is documented in docs/security.md.
BLOCKED_NETWORKS = [
    ipaddress.ip_network("169.254.169.254/32"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
]


def is_blocked_target(host: str) -> bool:
    """Reject loopback/private/metadata IPs when resolvable (SSRF mitigation)."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        for net in BLOCKED_NETWORKS:
            if ip in net:
                return True
    return False


class RemoteMonitor:
    def __init__(self, host, username, password, port=22, os_type="linux"):
        self.host = host
        self.username = username
        self.password = password
        self.port = int(port or 22)
        self.os_type = (os_type or "linux").lower()

    def _connect(self, timeout=8):
        if is_blocked_target(self.host):
            raise PermissionError("Target host is not allowed")
        client = paramiko.SSHClient()
        # Prefer known_hosts when present; fall back only for demo lab use.
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=timeout,
                banner_timeout=timeout,
                auth_timeout=timeout,
                allow_agent=False,
                look_for_keys=False,
            )
        except paramiko.SSHException:
            # Lab fallback: AutoAdd only after Reject failed due to unknown host.
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=timeout,
                banner_timeout=timeout,
                auth_timeout=timeout,
                allow_agent=False,
                look_for_keys=False,
            )
        return client

    def _exec(self, client, command, timeout=12):
        _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="ignore").strip()
        err = stderr.read().decode(errors="ignore").strip()
        return out, err

    def _run_allowlisted(self, commands: dict[str, str]) -> dict[str, str]:
        client = self._connect()
        try:
            results = {}
            for key, command in commands.items():
                out, _err = self._exec(client, command)
                results[key] = out
            return results
        finally:
            client.close()

    def get_all_stats(self):
        if self.os_type == "windows":
            return self._collect_windows()
        return self._collect_linux()

    def _collect_linux(self):
        raw = self._run_allowlisted(LINUX_COMMANDS)
        try:
            cpu_percent = round(float(raw.get("cpu") or 0), 1)
        except ValueError:
            cpu_percent = 0.0
        try:
            cpu_count = int((raw.get("cpu_count") or "0").split()[0])
        except (ValueError, IndexError):
            cpu_count = 0
        mem_parts = (raw.get("memory") or "").split()
        total = int(mem_parts[0]) if len(mem_parts) > 0 else 0
        used = int(mem_parts[1]) if len(mem_parts) > 1 else 0
        available = int(mem_parts[2]) if len(mem_parts) > 2 else 0
        disks = []
        for line in (raw.get("disk") or "").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            try:
                size, used_d, free = int(parts[2]), int(parts[3]), int(parts[4])
            except ValueError:
                continue
            percent = round((used_d / size) * 100, 1) if size else 0
            disks.append(
                {
                    "device": parts[0],
                    "mountpoint": parts[1],
                    "total": size,
                    "used": used_d,
                    "free": free,
                    "percent": percent,
                }
            )
        processes = []
        for line in (raw.get("processes") or "").splitlines()[1:]:
            parts = line.split(None, 4)
            if len(parts) < 5:
                continue
            try:
                processes.append(
                    {
                        "pid": int(parts[0]),
                        "name": parts[1],
                        "cpu_percent": float(parts[2]),
                        "memory_percent": float(parts[3]),
                        "status": parts[4],
                    }
                )
            except ValueError:
                continue
        return {
            "cpu": {"percent": cpu_percent, "count": cpu_count, "frequency": {"current": 0}},
            "memory": {
                "total": total,
                "used": used,
                "available": available,
                "percent": round((used / total) * 100, 1) if total else 0,
            },
            "disk": disks,
            "network": {"bytes_sent": 0, "bytes_recv": 0, "raw_present": bool(raw.get("network"))},
            "processes": processes,
            "host": self.host,
            "os_type": "linux",
        }

    def _collect_windows(self):
        raw = self._run_allowlisted(WINDOWS_COMMANDS)
        try:
            cpu_percent = float((raw.get("cpu") or "0").split()[0])
        except (ValueError, IndexError):
            cpu_percent = 0.0
        try:
            cpu_count = int((raw.get("cpu_count") or "0").split()[0])
        except (ValueError, IndexError):
            cpu_count = 0
        mem_lines = (raw.get("memory") or "").splitlines()
        try:
            total = int(mem_lines[0]) if len(mem_lines) > 0 else 0
            used = int(mem_lines[1]) if len(mem_lines) > 1 else 0
            available = int(mem_lines[2]) if len(mem_lines) > 2 else 0
        except ValueError:
            total = used = available = 0
        processes = []
        for line in (raw.get("processes") or "").splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                processes.append(
                    {
                        "pid": int(parts[0]),
                        "name": parts[1],
                        "cpu_percent": 0,
                        "memory_percent": 0,
                        "status": "running",
                    }
                )
        return {
            "cpu": {"percent": cpu_percent, "count": cpu_count, "frequency": {"current": 0}},
            "memory": {
                "total": total,
                "used": used,
                "available": available,
                "percent": round((used / total) * 100, 1) if total else 0,
            },
            "disk": [],
            "network": {"bytes_sent": 0, "bytes_recv": 0},
            "processes": processes,
            "host": self.host,
            "os_type": "windows",
        }


def tcp_probe(host: str, port: int, timeout: float = 3.0) -> tuple[bool, str]:
    """Shallow TCP connectivity check (no SSH auth)."""
    if not host or not (1 <= int(port) <= 65535):
        return False, "Invalid host or port"
    if is_blocked_target(host):
        return False, "Target host is not allowed"
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True, "TCP port reachable"
    except OSError:
        return False, "Connection failed"
