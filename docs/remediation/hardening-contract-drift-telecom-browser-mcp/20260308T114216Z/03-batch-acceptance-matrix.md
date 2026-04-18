# 03 Batch Acceptance Matrix

| Batch | Acceptance check | Result |
|---|---|---|
| B01 | `health` and `capabilities` covered by canonical contracts, schemas, and canonical envelope | pass |
| B01 | schema generation includes all registered tools | pass |
| B02 | broken browser-page path sets lifecycle state to `broken` | pass |
| B03 | evidence redaction masks secrets in strings and nested payloads | pass |
| B03 | stdio smoke skip behavior narrowed from broad catch-all | pass |
| All | static verification suite passes (`tests/unit`, `tests/contract`, server bootstrap integration) | pass |
