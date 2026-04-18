# Lifecycle State Map

## Implemented States
- `starting` (model default)
- `ready` (successful browser open)
- `degraded` (launch/environment-limited open)
- `broken` (explicit browser page missing path)
- `closing`
- `closed`

## Transition Evidence
- `starting -> ready|degraded`: `SessionManager.create`
- `* -> broken`: `ToolService._require_browser_page`
- `* -> closing -> closed`: `SessionManager.close`
