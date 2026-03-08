# Schema vs Signature Diff

Comparison dimensions:

- Observed pre-fix Codex-facing invocation shape: single `kwargs` wrapper field (runtime evidence).
- Post-fix registration shape: wrapper signature copied from orchestrator callable.
- Runtime behavior: in-process dispatch smoke and unit tests.

| Tool | Pre-fix status | Post-fix status | Required fields | Optional fields | Notes |
|---|---|---|---|---|---|
| health | broken | compatible | (none) | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| capabilities | broken | compatible | (none) | include_groups | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| open_app | broken | compatible | url | adapter_name | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| login_agent | broken | compatible | session_id, username, password | tenant | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| wait_for_ready | broken | compatible | session_id | timeout_ms | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| list_sessions | broken | compatible | (none) | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| close_session | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| reset_session | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_registration_status | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| wait_for_registration | broken | compatible | session_id | expected, timeout_ms | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| assert_registered | broken | compatible | session_id | timeout_ms | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| wait_for_incoming_call | broken | compatible | session_id | timeout_ms | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| answer_call | broken | compatible | session_id | timeout_ms | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| hangup_call | broken | compatible | session_id | timeout_ms | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_ui_call_state | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_active_session_snapshot | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_store_snapshot | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_peer_connection_summary | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_webrtc_stats | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| get_environment_snapshot | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| screenshot | broken | compatible | session_id | label | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| collect_browser_logs | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| collect_debug_bundle | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| diagnose_registration_failure | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| diagnose_incoming_call_failure | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| diagnose_answer_failure | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |
| diagnose_one_way_audio | broken | compatible | session_id | (none) | legacy kwargs unwrapped in dispatcher; signature-aligned wrapper in stdio registration |

## Severity classification

- `broken` (pre-fix): all tools were exposed through a synthetic `kwargs` path that could trigger invocation binding errors.
- `compatible` (post-fix): tool wrappers now expose orchestrator signatures and legacy payloads are normalized.
- `compatible_with_fix`: none remaining after this remediation batch.
