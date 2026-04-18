# Tool Catalog

| Tool | Description | Required Arguments | Optional Arguments |
|---|---|---|---|
| `answer_call` | Attempt to answer an incoming call. | session_id | timeout_ms |
| `capabilities` | Read-only capability discovery. | none | none |
| `close_session` | Close a managed session. | session_id | none |
| `collect_debug_bundle` | Capture structured troubleshooting artifacts. | session_id | reason |
| `diagnose_answer_failure` | Run answer-failure diagnostic classification. | session_id | none |
| `get_active_session_snapshot` | Read session-level runtime snapshot. | session_id | none |
| `get_peer_connection_summary` | Read WebRTC peer connection summary. | session_id | none |
| `health` | Read-only service health check. | none | none |
| `list_sessions` | List currently tracked sessions. | none | none |
| `login_agent` | Run adapter login flow. | session_id | credentials, timeout_ms |
| `open_app` | Create a telecom browser session. | target_url | adapter_id, headless, session_label |
| `wait_for_incoming_call` | Wait until an incoming call is observed. | session_id | timeout_ms |
| `wait_for_ready` | Wait until UI/app is ready. | session_id | timeout_ms |
| `wait_for_registration` | Wait until telecom registration is observed. | session_id | timeout_ms |

## Notes
- Example payloads are schema-valid and generated from canonical tool input models.
- Operational confidence is `verified` only for first-contact tools in this pipeline run.
