from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from telecom_browser_mcp.browser.url_policy import URLPolicy, URLPolicyError, validate_target_url

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext, Page, Playwright, Route
else:
    Browser = BrowserContext = Page = Playwright = Route = Any


@dataclass(frozen=True)
class BlockedBrowserRequest:
    url: str
    reason_code: str
    resource_type: str
    is_navigation_request: bool


class BrowserRequestGuard:
    def __init__(self, url_policy: URLPolicy | None = None) -> None:
        self._url_policy = url_policy
        self.blocked_requests: list[BlockedBrowserRequest] = []

    async def handle_route(self, route: Route, request: Any) -> None:
        try:
            validate_target_url(request.url, self._url_policy)
        except URLPolicyError as exc:
            self.blocked_requests.append(
                BlockedBrowserRequest(
                    url=exc.safe_target,
                    reason_code=exc.reason_code,
                    resource_type=getattr(request, "resource_type", "unknown"),
                    is_navigation_request=bool(
                        getattr(request, "is_navigation_request", lambda: False)()
                    ),
                )
            )
            await route.abort("blockedbyclient")
            return
        await route.continue_()


@dataclass
class BrowserHandle:
    browser_open: bool
    launch_error: str | None = None
    launch_error_classification: str | None = None
    target_url: str | None = None
    playwright: Playwright | None = None
    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None
    request_guard: BrowserRequestGuard | None = None
    blocked_requests: list[BlockedBrowserRequest] = field(default_factory=list)


class BrowserManager:
    def __init__(self, url_policy: URLPolicy | None = None) -> None:
        self._url_policy = url_policy

    async def open(self, target_url: str, headless: bool = True) -> BrowserHandle:
        target_url = validate_target_url(target_url, self._url_policy)
        handle = BrowserHandle(browser_open=False, target_url=target_url)
        playwright: Playwright | None = None
        browser: Browser | None = None
        context: BrowserContext | None = None
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=headless)
            context = await browser.new_context()
            request_guard = BrowserRequestGuard(self._url_policy)
            await context.route("**/*", request_guard.handle_route)
            page = await context.new_page()
            await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
            if request_guard.blocked_requests:
                blocked = request_guard.blocked_requests[0]
                raise RuntimeError(
                    "browser request blocked by URL policy: "
                    f"{blocked.reason_code} {blocked.url}"
                )

            handle.playwright = playwright
            handle.browser = browser
            handle.context = context
            handle.page = page
            handle.request_guard = request_guard
            handle.blocked_requests = request_guard.blocked_requests
            handle.browser_open = True
            return handle
        except Exception as exc:  # pragma: no cover - environment dependent
            message = str(exc)
            classification = "unknown"
            lowered = message.lower()
            if "executable doesn't exist" in lowered or "browser" in lowered and "install" in lowered:
                classification = "environment_limit_missing_browser_binary"
            elif "permission" in lowered or "sandbox" in lowered:
                classification = "permission_blocked"
            elif "browser request blocked by url policy" in lowered:
                classification = "security_policy"
            elif "net::" in lowered or "timed out" in lowered:
                classification = "environment_limit_unreachable_target"
            handle.launch_error = message
            handle.launch_error_classification = classification
            if context is not None and "request_guard" in locals():
                handle.blocked_requests = request_guard.blocked_requests
            if context is not None:
                await context.close()
            if browser is not None:
                await browser.close()
            if playwright is not None:
                await playwright.stop()
            return handle

    async def close(self, handle: BrowserHandle) -> None:
        if handle.context is not None:
            await handle.context.close()
        if handle.browser is not None:
            await handle.browser.close()
        if handle.playwright is not None:
            await handle.playwright.stop()
        handle.browser_open = False
