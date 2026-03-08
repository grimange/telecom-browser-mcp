from __future__ import annotations

from urllib.parse import urlparse

from telecom_browser_mcp.adapters.base import AdapterBase
from telecom_browser_mcp.adapters.generic import GenericAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, type[AdapterBase]] = {
            GenericAdapter.adapter_id: GenericAdapter,
        }
        self._domain_map: dict[str, str] = {}

    def register(self, adapter_cls: type[AdapterBase], domains: list[str] | None = None) -> None:
        self._adapters[adapter_cls.adapter_id] = adapter_cls
        for domain in domains or []:
            self._domain_map[domain] = adapter_cls.adapter_id

    def resolve(self, target_url: str, adapter_id: str | None = None) -> tuple[AdapterBase, str, float]:
        if adapter_id:
            if adapter_id in self._adapters:
                return self._adapters[adapter_id](), "explicit", 1.0
            raise KeyError(adapter_id)

        host = (urlparse(target_url).hostname or "").lower()
        if host in self._domain_map:
            resolved = self._domain_map[host]
            return self._adapters[resolved](), "domain_map", 0.95

        return GenericAdapter(), "fallback", 0.5
