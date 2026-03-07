class SipInspector:
    async def get_registration_snapshot(self, adapter, session):
        return await adapter.get_registration_snapshot(session)

    async def get_active_session_snapshot(self, adapter, session):
        return await adapter.get_active_session_snapshot(session)
