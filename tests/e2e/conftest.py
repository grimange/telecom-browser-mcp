from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "host_required: test requires host Playwright/browser runtime; may skip in constrained environments",
    )
