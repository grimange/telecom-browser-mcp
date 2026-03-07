# Artifact Schema (20260307T131300Z)

Per bundle directory:

- `manifest.json`
- `summary.md`
- `console.json`
- `network.json`
- `page-errors.json`
- `metadata.json`
- `screenshot.png` (if available)
- `dom.html` (if available)
- `trace.zip` (if available)

## JSON Shapes
- `console.json`: `{ "events": [ {timestamp, level, text, location} ] }`
- `page-errors.json`: `{ "events": [ {timestamp, message} ] }`
- `network.json`: `{ "requests": [...], "responses": [...], "failures": [...] }`
- `metadata.json`: includes run/session/scenario/fault/injection/state and page/context ids.
- `manifest.json`: references artifact paths, timing markers, and collection gaps.
