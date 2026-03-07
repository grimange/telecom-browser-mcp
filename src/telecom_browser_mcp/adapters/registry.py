from telecom_browser_mcp.adapters.apntalk import ApnTalkAdapter
from telecom_browser_mcp.adapters.generic_jssip import GenericJsSipAdapter
from telecom_browser_mcp.adapters.generic_sipjs import GenericSipJsAdapter
from telecom_browser_mcp.adapters.harness import HarnessAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters = {
            "generic_sipjs": GenericSipJsAdapter,
            "generic_jssip": GenericJsSipAdapter,
            "apntalk": ApnTalkAdapter,
            "harness": HarnessAdapter,
        }

    def create(self, adapter_name: str):
        adapter_cls = self._adapters.get(adapter_name)
        if adapter_cls is None:
            raise ValueError(f"unknown adapter: {adapter_name}")
        return adapter_cls()

    def names(self) -> list[str]:
        return sorted(self._adapters.keys())
