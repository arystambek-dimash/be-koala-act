import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class VillagePassage(Base):
    __tablename__ = 'village_passages'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    description: orm.Mapped[str] = orm.mapped_column(sa.TEXT)
    parent_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey('village_passages.id', ondelete="CASCADE"),
        nullable=True
    )
    village_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('villages.id', ondelete="CASCADE"))
    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer)
