# 07 Adapter Boundary Audit

## Result
- Telecom UI selectors and DOM assumptions are concentrated in adapter modules (`fake_dialer`, `apntalk`).
- Core tool/session/browser layers do not contain adapter-specific selectors.

## Evidence
- Selectors (`#app-ready`, `#answer-btn`, etc.) are only found in `src/telecom_browser_mcp/adapters/fake_dialer.py`.
- APNTalk adapter remains conservative and does not claim unsupported runtime paths.

No adapter boundary violations detected.
