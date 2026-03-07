from enum import Enum


class BrowserSessionState(str, Enum):
    ACTIVE = "active"
    CLOSING = "closing"
    CLOSED = "closed"
    BROKEN = "broken"


class RegistrationState(str, Enum):
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    CONNECTING = "connecting"
    REGISTERED = "registered"
    FAILED = "failed"


class CallState(str, Enum):
    IDLE = "idle"
    RINGING = "ringing"
    ANSWERING = "answering"
    CONNECTED = "connected"
    ENDING = "ending"
    ENDED = "ended"
    FAILED = "failed"


class WebRtcState(str, Enum):
    MISSING = "missing"
    NEW = "new"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    CLOSED = "closed"


class FailureCategory(str, Enum):
    SESSION = "session"
    REGISTRATION = "registration"
    CALL_CONTROL = "call_control"
    INSPECTION = "inspection"
    DIAGNOSTIC = "diagnostic"
    ENVIRONMENT = "environment"
    ADAPTER = "adapter"


class ErrorCode(str, Enum):
    UI_SELECTOR_FAILURE = "UI_SELECTOR_FAILURE"
    APP_NOT_READY = "APP_NOT_READY"
    REGISTRATION_TIMEOUT = "REGISTRATION_TIMEOUT"
    INCOMING_CALL_TIMEOUT = "INCOMING_CALL_TIMEOUT"
    ANSWER_FLOW_FAILED = "ANSWER_FLOW_FAILED"
    PEER_CONNECTION_MISSING = "PEER_CONNECTION_MISSING"
    WEBRTC_STATE_UNAVAILABLE = "WEBRTC_STATE_UNAVAILABLE"
    ADAPTER_CONTRACT_ERROR = "ADAPTER_CONTRACT_ERROR"
    BROWSER_SESSION_BROKEN = "BROWSER_SESSION_BROKEN"
    ENVIRONMENT_LIMITATION = "ENVIRONMENT_LIMITATION"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    UNKNOWN = "UNKNOWN"
