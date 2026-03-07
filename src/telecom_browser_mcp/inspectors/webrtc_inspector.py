class WebRtcInspector:
    async def get_summary(self, adapter, session):
        return await adapter.get_peer_connection_summary(session)

    async def get_stats(self, adapter, session) -> dict:
        summary = await adapter.get_peer_connection_summary(session)
        return {
            "available": summary.available,
            "peer_connection_present": summary.peer_connection_present,
            "inbound_rtp_audio_packets": summary.inbound_rtp_audio_packets,
            "outbound_rtp_audio_packets": summary.outbound_rtp_audio_packets,
            "timestamp": summary.timestamp,
        }
