from typing import Generic, TypeVar, Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self._session.get(self.model, id)

    async def get_all(
            self,
            limit: int = 100,
            offset: int = 0,
            order_field: str | None = None,
            order_type: str = "asc",  # "asc" | "desc"
    ) -> Sequence[ModelType]:
        stmt = select(self.model)

        if order_field:
            field = getattr(self.model, order_field, None)
            if field is None:
                raise ValueError(f"Unknown order_field: {order_field}")

            order_type_l = order_type.lower()
            if order_type_l not in ("asc", "desc"):
                raise ValueError(f"Unknown order_type: {order_type}")

            stmt = stmt.order_by(field.desc() if order_type_l == "desc" else field.asc())

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        stmt = insert(self.model).values(**kwargs).returning(self.model)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def update(self, id: int, **kwargs) -> ModelType | None:
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0
