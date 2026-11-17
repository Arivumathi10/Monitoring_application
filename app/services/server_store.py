"""Encrypted persistence for managed SSH server targets."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

HOST_RE = re.compile(r"^[A-Za-z0-9._:-]{1,253}$")
VALID_OS = frozenset({"linux", "windows"})


class ServerStore:
    """JSON file store with Fernet-encrypted SSH passwords."""

    def __init__(self, storage_path: str | None = None, key_material: str | None = None):
        self.storage_path = storage_path or "app/servers.json"
        self._fernet = self._build_fernet(key_material)
        parent = os.path.dirname(self.storage_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save({})
            try:
                os.chmod(self.storage_path, 0o600)
            except OSError:
                pass

    @staticmethod
    def _build_fernet(key_material: str | None) -> Fernet:
        material = key_material or os.getenv("SERVERS_KEY") or ""
        if not material:
            raise RuntimeError("SERVERS_KEY must be set to encrypt server credentials.")
        digest = hashlib.sha256(material.encode("utf-8")).digest()
        return Fernet(base64.urlsafe_b64encode(digest))

    def _encrypt(self, value: str | None) -> str | None:
        if not value:
            return None
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def _decrypt(self, value: str | None) -> str | None:
        if not value:
            return None
        try:
            return self._fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except (InvalidToken, ValueError, TypeError):
            return None

    def _load(self) -> dict[str, Any]:
        with open(self.storage_path, encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, data: dict[str, Any]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        try:
            os.chmod(self.storage_path, 0o600)
        except OSError:
            pass

    @staticmethod
    def validate_host(host: str) -> bool:
        return bool(host and HOST_RE.match(host) and ".." not in host)

    @staticmethod
    def validate_port(port: int) -> bool:
        return isinstance(port, int) and 1 <= port <= 65535

    def add_server(self, server: dict[str, Any]) -> bool:
        data = self._load()
        host = server["host"]
        if host in data:
            return False
        record = dict(server)
        record["password"] = self._encrypt(record.get("password"))
        data[host] = record
        self._save(data)
        return True

    def update_server(self, host: str, updates: dict[str, Any]) -> bool:
        data = self._load()
        if host not in data:
            return False
        payload = dict(updates)
        if payload.get("password"):
            payload["password"] = self._encrypt(payload["password"])
        elif "password" in payload:
            payload.pop("password")
        data[host].update(payload)
        self._save(data)
        return True

    def remove_server(self, host: str) -> bool:
        data = self._load()
        if host not in data:
            return False
        del data[host]
        self._save(data)
        return True

    def get_server(self, host: str, with_credentials: bool = False) -> dict[str, Any] | None:
        data = self._load()
        server = data.get(host)
        if not server:
            return None
        item = dict(server)
        item["host"] = host
        if with_credentials:
            item["password"] = self._decrypt(item.get("password"))
        else:
            item.pop("password", None)
        return item

    def list_servers(self, os_type: str | None = None) -> list[dict[str, Any]]:
        data = self._load()
        servers = []
        for host, server in data.items():
            item = dict(server)
            item["host"] = host
            item.pop("password", None)
            if os_type and item.get("os_type") != os_type:
                continue
            servers.append(item)
        return servers


def get_store() -> ServerStore:
    path = current_app.config.get("SERVERS_FILE", "app/servers.json")
    key = current_app.config.get("SERVERS_KEY")
    return ServerStore(storage_path=path, key_material=key)
