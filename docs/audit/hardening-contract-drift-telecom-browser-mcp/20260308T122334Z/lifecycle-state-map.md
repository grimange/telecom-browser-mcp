# Lifecycle State Map

States observed:
- `starting`
- `ready`
- `degraded`
- `broken`
- `closing`
- `closed`

Transitions:
- `starting -> ready|degraded` (session create)
- `* -> broken` (page missing guard)
- `* -> closing -> closed` (session close)
