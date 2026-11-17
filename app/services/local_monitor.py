"""Local host collector using psutil (Linux/macOS/Windows)."""
import psutil

from app.services.base_monitor import BaseMonitor


class LocalMonitor(BaseMonitor):
    def get_cpu_usage(self):
        freq = psutil.cpu_freq()
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count() or 0,
            "frequency": {
                "current": freq.current if freq else 0,
                "min": freq.min if freq else 0,
                "max": freq.max if freq else 0,
            },
        }

    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent,
        }

    def get_disk_usage(self):
        partitions = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except (PermissionError, OSError):
                continue
            partitions.append(
                {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            )
        return partitions

    def get_network_usage(self):
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

    def get_top_processes(self, limit=10):
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                info = proc.info
                processes.append(
                    {
                        "pid": info.get("pid"),
                        "name": info.get("name") or "",
                        "cpu_percent": info.get("cpu_percent") or 0.0,
                        "memory_percent": round(info.get("memory_percent") or 0.0, 2),
                        "status": info.get("status") or "",
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        processes.sort(key=lambda p: p["cpu_percent"], reverse=True)
        return processes[:limit]


def get_local_monitor():
    return LocalMonitor()
