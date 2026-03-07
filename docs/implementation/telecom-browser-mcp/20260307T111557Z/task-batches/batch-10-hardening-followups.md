# Batch 10 Hardening Followups

## Priority follow-ups
1. Implement strict origin allowlist enforcement in navigation and adapter open flow.
2. Add adapter-level selector/runtime assumption manifests and compatibility versions.
3. Expand evidence redaction (screenshots + log payload fields).
4. Add artifact retention/cleanup policy tooling.
5. Add explicit retry budgets/timeouts per tool and adapter.
6. Add live-host transport verification matrix (stdio + streamable-http + optional sse).
7. Add APNTalk real adapter implementation with regression tests.

## Validation target
- Keep `python -m pytest -q` green while expanding adapter depth.
