from sqlalchemy.ext.asyncio import AsyncSession


class UoW:
    """
    Unit of Work pattern for grouping database operations.
    Note: Commit/rollback is handled by the session dependency.
    UoW only flushes changes to ensure they're visible within the transaction.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self._session.flush()
