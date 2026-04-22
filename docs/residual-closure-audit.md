# Residual Closure Audit

## A1 Secondary Request Egress Governance

Classification: `PARTIALLY_CLOSABLE`

Current state before closure: initial `open_app.target_url` validation blocked unsafe schemes, unsafe DNS results, local/private/link-local/reserved/multicast/metadata targets, and non-allowlisted hosts before `page.goto`. That left residual exposure for browser-issued requests after the initial navigation.

Repo-native closure: Playwright `BrowserContext.route("**/*", ...)` can safely apply the same URL policy to requests surfaced by Playwright without changing public MCP tool contracts. The bounded guard now aborts blocked requests and records sanitized metadata. Requests blocked during initial load make `open_app` fail closed with `target_url_blocked`; requests blocked after a session opens cause the next browser-dependent tool to fail closed and mark the session broken.

Residual boundary: this does not claim governance for browser-internal requests that Playwright does not expose, non-HTTP browser internals, or deployment-layer network egress. Host/network firewalls remain required for production defense in depth.

## A2 Live Transport Runtime Verification Gap

Classification: `ENVIRONMENT_BLOCKED`

The live transport tests require subprocess startup and loopback socket creation. In this sandbox, loopback socket creation previously failed with `PermissionError: Operation not permitted`, and stdio first contact timed out when live runtime was required. The tests should not be weakened to pass in this environment because they are intended to verify real transport behavior on a host-capable runtime.

Closure action: docs now include the exact host-capable live command and classify sandbox socket/process failures as environment limitations. CI retains the live transport job with `MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`.

## A3 Screenshot Sensitivity Closure

Classification: `DESIGNALLY_RETAINED_WITH_GUARDS`

Screenshots are pixel artifacts and are not text-redacted. Pixel-level redaction is not implemented or claimed.

Closure action: non-harness screenshots remain disabled by default, harness screenshots remain available for deterministic tests, omitted screenshots include reason text, and bundle manifests include sensitivity metadata stating screenshots are sensitive and `screenshot_pixel_redaction` is false.
