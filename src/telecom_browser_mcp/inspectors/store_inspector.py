class StoreInspector:
    async def get_snapshot(self, adapter, session) -> dict:
        return await adapter.get_store_snapshot(session)
