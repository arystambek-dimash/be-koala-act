from sqlalchemy import select, func, update
from sqlalchemy.dialects.postgresql import insert

from src.app.constants import FundType
from src.models.wallets import Wallet
from src.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    model = Wallet

    async def get_by_user_id(self, user_id: int) -> list[dict]:
        stmt = (
            select(Wallet.fund_type, func.sum(Wallet.fund))
            .where(Wallet.user_id == user_id)
            .group_by(Wallet.fund_type)
        )
        result = await self._session.execute(stmt)
        return [
            {"fund_type": row[0], "fund": row[1]}
            for row in result.all()
        ]

    async def get_balance(self, user_id: int, fund_type: FundType) -> int:
        stmt = (
            select(func.coalesce(func.sum(Wallet.fund), 0))
            .where(Wallet.user_id == user_id, Wallet.fund_type == fund_type)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def add_funds(self, user_id: int, amount: int, fund_type: FundType) -> Wallet:
        """Add funds to user's wallet. Creates wallet entry if not exists."""
        stmt = (
            insert(Wallet)
            .values(user_id=user_id, fund=amount, fund_type=fund_type)
            .returning(Wallet)
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def deduct_funds(self, user_id: int, amount: int, fund_type: FundType) -> bool:
        """Deduct funds from user's wallet. Returns False if insufficient balance."""
        current_balance = await self.get_balance(user_id, fund_type)
        if current_balance < amount:
            return False

        # Add negative transaction
        await self.add_funds(user_id, -amount, fund_type)
        return True

    async def has_sufficient_funds(self, user_id: int, amount: int, fund_type: FundType) -> bool:
        balance = await self.get_balance(user_id, fund_type)
        return balance >= amount
