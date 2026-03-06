# telecom-browser-mcp

**Telecom-aware browser MCP server for testing and debugging WebRTC softphones and dialer UIs.**

`telecom-browser-mcp` is a Model Context Protocol (MCP) server that enables AI agents to automate, inspect, and diagnose telecom web applications such as browser softphones, WebRTC dialers, and ARI-driven call platforms.

Unlike generic browser automation tools, this MCP server exposes **telecom domain operations** like:

- `wait_for_incoming_call`
- `answer_call`
- `get_registration_status`
- `get_peer_connection_summary`
- `diagnose_answer_failure`

This allows AI agents to reason about **telecom behavior**, not just DOM interactions.

The project is built using the **official MCP Python SDK** and **Playwright**.

---

# Why This Project Exists

Testing telecom browser applications is hard because problems occur across multiple layers:

| Layer | Example Problems |
|-----|-----|
| UI | incoming call popup not appearing |
| App State | frontend store stuck in RINGING |
| SIP/WebRTC | session terminated unexpectedly |
| Media | peer connection exists but no RTP |
| Backend | ARI event delivered but UI ignored it |

Traditional tools only see part of the system.

| Tool | Visibility |
|----|----|
| Selenium / Playwright | UI only |
| SIP tools | signaling only |
| PBX logs | backend only |

`telecom-browser-mcp` bridges the gap by allowing AI agents to inspect **UI, SIP runtime, and WebRTC state together**.

---

# Key Capabilities

## Browser Automation
Automate telecom web applications using Playwright.

Examples:

- open dialer UI
- login agent
- click answer button
- dial numbers
- capture screenshots

## SIP / WebRTC Runtime Inspection

Inspect telecom runtime state inside the browser.

Examples:

- SIP registration status
- active SIP session state
- WebSocket connectivity
- WebRTC peer connections
- ICE connection state
- inbound/outbound RTP stats

## Call Flow Interaction

Perform telecom actions directly through the UI.

Supported operations:

- dial
- answer
- hangup
- mute / unmute
- hold / resume

## Diagnostics

Detect and explain common telecom failures.

Examples:

- incoming call visible but no session object
- answered but backend never confirmed
- peer connection created but no audio tracks

## Debug Bundles

Automatically collect artifacts:

- screenshots
- console logs
- network traces
- runtime snapshots
- WebRTC statistics

These are persisted for CI pipelines and audits.

---

# Architecture

```
AI Agent (Codex / Claude)
        |
        v
telecom-browser-mcp
        |
        |--- Playwright Browser Driver
        |
        |--- Runtime Inspectors
        |      • UI Inspector
        |      • Store Inspector
        |      • SIP Inspector
        |      • WebRTC Inspector
        |
        |--- Diagnostics Engine
        |
        |--- Evidence Collector
```

Optionally integrate with:

```
telecom-mcp (PBX)
     |
     |--- ARI
     |--- AMI
     |--- Redis state
```

This allows full **end-to-end telecom verification**.

---

# Example MCP Tools

## Session Management

- `open_app(url)`
- `login_agent(username, password)`
- `wait_for_ready()`
- `reset_session()`

## Registration

- `get_registration_status()`
- `wait_for_registration()`
- `assert_registered()`

## Call Operations

- `dial(number)`
- `wait_for_incoming_call()`
- `answer_call()`
- `hangup_call()`

## Runtime Inspection

- `get_store_snapshot()`
- `get_active_session_snapshot()`
- `get_peer_connection_summary()`
- `get_webrtc_stats()`

## Diagnostics

- `diagnose_registration_failure()`
- `diagnose_incoming_call_failure()`
- `diagnose_answer_failure()`

## Evidence

- `screenshot()`
- `collect_browser_logs()`
- `collect_debug_bundle()`

---

# Example Usage

Example call flow verification:

```
open_app()
login_agent()
wait_for_registration()

wait_for_incoming_call()
answer_call()

assert_call_state("connected")

get_peer_connection_summary()

hangup_call()
```

---

# Installation

Clone repository:

```
git clone https://github.com/your-org/telecom-browser-mcp.git
cd telecom-browser-mcp
```

Install dependencies:

```
pip install -e .
playwright install
```

Run MCP server:

```
python -m telecom_browser_mcp.server
```

---

# Example Project Structure

```
telecom-browser-mcp
│
├─ src/
│   ├─ server/
│   │   └─ mcp_server.py
│   │
│   ├─ browser/
│   │   ├─ playwright_driver.py
│   │   └─ browser_session.py
│   │
│   ├─ adapters/
│   │   ├─ base_adapter.py
│   │   └─ apntalk_adapter.py
│   │
│   ├─ inspectors/
│   │   ├─ sip_inspector.py
│   │   ├─ store_inspector.py
│   │   └─ webrtc_inspector.py
│   │
│   ├─ diagnostics/
│   │   ├─ answer_failure.py
│   │   └─ registration_failure.py
│   │
│   └─ evidence/
│       └─ debug_bundle.py
│
├─ tests/
│
├─ docs/
│
└─ README.md
```

---

# Adapters

Adapters allow the MCP server to support different dialer platforms.

Example adapters:

- APNTalk
- SIP.js softphones
- JsSIP dialers
- generic WebRTC softphones

Adapters define:

- UI selectors
- login flows
- store access paths
- runtime session models

---

# CI / Automation Use Cases

telecom-browser-mcp is designed for:

- AI-driven debugging
- CI telecom UI testing
- dialer regression tests
- WebRTC troubleshooting
- contract verification between backend and frontend

---

# Related Projects

Often used together with:

- `telecom-mcp`
- ARI / AMI automation
- Asterisk-based platforms
- WebRTC dialer platforms

---

# Roadmap

Planned features:

- conference support
- transfer testing
- multi-call sessions
- contract validation mode
- SIP trace integration
- WebRTC media quality checks

---

# License

MIT License

---

# Contributing

Contributions are welcome.

Please open an issue or discussion before major changes.

---

# Acknowledgements

Built using:

- Model Context Protocol Python SDK
- Playwright
- WebRTC
- SIP-based telecom systems
