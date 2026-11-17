"""Abstract monitor interface.

Safe-to-expose fields: CPU/memory/disk/network aggregates, listening ports
(address + status), and process name/pid/cpu/mem percentages.
Never expose: env vars, file contents, credentials, full argv if sensitive.
"""
from abc import ABC, abstractmethod


class BaseMonitor(ABC):
    @abstractmethod
    def get_cpu_usage(self):
        pass

    @abstractmethod
    def get_memory_usage(self):
        pass

    @abstractmethod
    def get_disk_usage(self):
        pass

    @abstractmethod
    def get_network_usage(self):
        pass

    @abstractmethod
    def get_top_processes(self, limit=10):
        pass

    def get_all_stats(self):
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_usage(),
            "processes": self.get_top_processes(),
        }
