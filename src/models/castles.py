import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Castle(Base):
    __tablename__ = 'castles'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    svg: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=True)
    treasure_capacity: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=300)
    speed_production_treasure: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=1)
    cost: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        nullable=True
    )  # тут будет у замков система уровень это цена для перехода следующего
    parent_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('castles.id'), default=0)
    is_first_castle: bool = orm.mapped_column(sa.Boolean, default=False)
