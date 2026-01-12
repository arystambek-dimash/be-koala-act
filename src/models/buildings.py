import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.constants import BuildingType
from src.app.database import Base


class Building(Base):
    __tablename__ = 'buildings'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    svg: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=True)
    treasure_capacity: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=300)
    speed_production_treasure: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=1)
    cost: orm.Mapped[int | None] = orm.mapped_column(
        sa.Integer,
        nullable=True
    )  # тут будет у замков система уровень это цена для перехода следующего
    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=1)
    type: orm.Mapped[BuildingType] = orm.mapped_column(sa.Enum(BuildingType))
