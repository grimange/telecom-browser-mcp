from __future__ import annotations

from urllib.parse import urlparse

from telecom_browser_mcp.adapters.base import AdapterBase
from telecom_browser_mcp.adapters.generic import GenericAdapter


class AdapterTargetMismatchError(ValueError):
    def __init__(self, requested_adapter_id: str, expected_adapter_id: str, host: str) -> None:
        self.requested_adapter_id = requested_adapter_id
        self.expected_adapter_id = expected_adapter_id
        self.host = host
        super().__init__(
            f"target host '{host}' is mapped to adapter '{expected_adapter_id}', not '{requested_adapter_id}'"
        )


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

    def descriptors(self) -> list[dict[str, object]]:
        descriptors: list[dict[str, object]] = []
        domains_by_adapter: dict[str, list[str]] = {}
        for domain, adapter_id in self._domain_map.items():
            domains_by_adapter.setdefault(adapter_id, []).append(domain)

        for adapter_id, adapter_cls in sorted(self._adapters.items()):
            adapter = adapter_cls()
            descriptors.append(
                {
                    "adapter_id": adapter.adapter_id,
                    "adapter_name": adapter.adapter_name,
                    "adapter_version": adapter.adapter_version,
                    "contract_version": adapter.contract_version,
                    "scenario_id": adapter.scenario_id,
                    "support_status": adapter.support_status,
                    "capabilities": adapter.capabilities.model_dump(mode="json"),
                    "capability_truth": adapter.capability_truth(),
                    "domains": sorted(domains_by_adapter.get(adapter_id, [])),
                }
            )
        return descriptors

    def resolve(self, target_url: str, adapter_id: str | None = None) -> tuple[AdapterBase, str, float]:
        host = (urlparse(target_url).hostname or "").lower()
        if adapter_id:
            mapped_adapter_id = self._domain_map.get(host)
            if mapped_adapter_id is not None and mapped_adapter_id != adapter_id:
                raise AdapterTargetMismatchError(
                    requested_adapter_id=adapter_id,
                    expected_adapter_id=mapped_adapter_id,
                    host=host,
                )
            if adapter_id in self._adapters:
                return self._adapters[adapter_id](), "explicit", 1.0
            raise KeyError(adapter_id)

        if host in self._domain_map:
            resolved = self._domain_map[host]
            return self._adapters[resolved](), "domain_map", 0.95

        return GenericAdapter(), "fallback", 0.5
