from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class LifecycleFaultError(RuntimeError):
    """Raised when a synthetic lifecycle fault is injected."""

    def __init__(self, injection_point: str, message: str) -> None:
        super().__init__(message)
        self.injection_point = injection_point
        self.message = message


@dataclass(slots=True)
class FaultTrigger:
    injection_point: str
    action: str
    once: bool = True
    message: str = "synthetic lifecycle fault injected"


class LifecycleFaultInjector:
    """Deterministic trigger-based fault injector for lifecycle tests."""

    def __init__(self) -> None:
        self._triggers: dict[str, list[FaultTrigger]] = {}

    def register(
        self,
        injection_point: str,
        action: str,
        *,
        once: bool = True,
        message: str = "synthetic lifecycle fault injected",
    ) -> None:
        trigger = FaultTrigger(
            injection_point=injection_point,
            action=action,
            once=once,
            message=message,
        )
        self._triggers.setdefault(injection_point, []).append(trigger)

    def emit(self, injection_point: str, target: Any | None = None) -> bool:
        triggers = self._triggers.get(injection_point)
        if not triggers:
            return False

        fired = False
        remaining: list[FaultTrigger] = []
        for trigger in triggers:
            self._apply(trigger, target)
            fired = True
            if not trigger.once:
                remaining.append(trigger)
        if remaining:
            self._triggers[injection_point] = remaining
        else:
            self._triggers.pop(injection_point, None)
        return fired

    def clear(self) -> None:
        self._triggers.clear()

    def _apply(self, trigger: FaultTrigger, target: Any | None) -> None:
        action = trigger.action
        if action == "close_browser":
            _mark_closed(target, "browser_closed")
            return
        if action == "close_context":
            _mark_closed(target, "context_closed")
            return
        if action == "close_page":
            _mark_closed(target, "page_closed")
            return
        if action == "stale_selector":
            _mark_stale_selector(target)
            return
        if action == "invalidate_registry":
            _mark_closed(target, "registry_invalid")
            return
        if action == "raise":
            raise LifecycleFaultError(trigger.injection_point, trigger.message)
        raise ValueError(f"unknown fault action: {action}")


def _mark_closed(target: Any | None, attr: str) -> None:
    if target is None:
        return
    if isinstance(target, dict):
        target[attr] = True
        return
    setattr(target, attr, True)


def _mark_stale_selector(target: Any | None) -> None:
    if target is None:
        return
    if isinstance(target, dict):
        target["dom_epoch"] = int(target.get("dom_epoch", 0)) + 1
        return
    if hasattr(target, "dom_epoch"):
        target.dom_epoch += 1
