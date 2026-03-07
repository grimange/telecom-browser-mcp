from datetime import datetime, timezone

from pydantic import BaseModel, Field

from telecom_browser_mcp.models.enums import WebRtcState


class WebRtcSnapshot(BaseModel):
    peer_connection_present: bool = False
    connection_state: WebRtcState = WebRtcState.MISSING
    ice_connection_state: str | None = None
    signaling_state: str | None = None
    local_audio_tracks: int = 0
    remote_audio_tracks: int = 0
    candidate_pair_state: str | None = None
    inbound_rtp_audio_packets: int | None = None
    outbound_rtp_audio_packets: int | None = None
    available: bool = True
    reason: str | None = None
    source: str = "adapter"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
