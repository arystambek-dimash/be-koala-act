import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Passage(Base):
    __tablename__ = "roadmap_passages"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    village_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("buildings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    title: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)

    nodes = orm.relationship(
        "PassageNode",
        back_populates="passage",
        cascade="all, delete-orphan",
        single_parent=True,
        order_by="PassageNode.order_index",
    )

    boss = orm.relationship(
        "PassageBoss",
        back_populates="passage",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
    )

    __table_args__ = (
        sa.UniqueConstraint("village_id", "order_index", name="uq_passage_village_order"),
        sa.Index("ix_passage_village_order", "village_id", "order_index"),
    )
