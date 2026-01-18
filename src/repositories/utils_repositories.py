from sqlalchemy import select, update


class UtilsRepository:
    async def reorder(
            self,
            item_id: int,
            new_index: int,
            fk_name: str | None = None,
            fk_id: int | None = None,
    ):
        if not self._session:
            raise RuntimeError("Session is not active")
        if not self.model:
            raise RuntimeError("Model is not active")

        if fk_name and fk_id:
            old_index = await self._session.scalar(
                select(self.model.order_index)
                .where(
                    self.model.id == item_id,
                    getattr(self.model, fk_name) == fk_id,
                )
            )
        else:
            old_index = await self._session.scalar(
                select(self.model.order_index)
                .where(
                    self.model.id == item_id
                )
            )
        if old_index is None:
            old_index = -1
        if new_index == old_index:
            return

        if fk_name and fk_id:
            await self._session.execute(
                update(self.model)
                .where(self.model.id == item_id, getattr(self.model, fk_name) == fk_id)
                .values(order_index=-1)
            )
        else:
            await self._session.execute(
                update(self.model)
                .where(self.model.id == item_id)
                .values(order_index=-1)
            )

        if new_index < old_index:
            if fk_name and fk_id:
                await self._session.execute(
                    update(self.model)
                    .where(
                        getattr(self.model, fk_name) == fk_id,
                        self.model.order_index >= new_index,
                        self.model.order_index < old_index,
                    )
                    .values(order_index=self.model.order_index + 1)
                )
            else:
                await self._session.execute(
                    update(self.model)
                    .where(
                        self.model.order_index >= new_index,
                        self.model.order_index < old_index,
                    )
                    .values(order_index=self.model.order_index + 1)
                )

        else:
            if fk_name and fk_id:
                await self._session.execute(
                    update(self.model)
                    .where(
                        getattr(self.model, fk_name) == fk_id,
                        self.model.order_index > old_index,
                        self.model.order_index <= new_index,
                    )
                    .values(order_index=self.model.order_index - 1)
                )
            else:
                await self._session.execute(
                    update(self.model)
                    .where(
                        self.model.order_index > old_index,
                        self.model.order_index <= new_index,
                    )
                    .values(order_index=self.model.order_index - 1)
                )
        if fk_name and fk_id:
            await self._session.execute(
                update(self.model)
                .where(self.model.id == item_id, getattr(self.model, fk_name) == fk_id)
                .values(order_index=new_index)
            )
        else:
            await self._session.execute(
                update(self.model)
                .where(self.model.id == item_id)
                .values(order_index=new_index)
            )
