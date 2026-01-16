import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.constants import SubjectEnum
from src.app.database import Base


class Passage(Base):
    __tablename__ = "roadmap_passages"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    village_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("buildings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    subject: orm.Mapped[SubjectEnum] = orm.mapped_column(
        sa.Enum(SubjectEnum),
        nullable=False,
        index=True,
    )

    title: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)

    nodes = orm.relationship(
        "PassageNode",
        primaryjoin="and_(Passage.id==PassageNode.passage_id, PassageNode.is_boss==False)",
        back_populates="passage",
        cascade="all, delete-orphan",
        order_by="PassageNode.order_index.asc()",
        overlaps="boss",
    )

    boss = orm.relationship(
        "PassageNode",
        primaryjoin="and_(Passage.id==PassageNode.passage_id, PassageNode.is_boss==True)",
        uselist=False,
        viewonly=True,
        overlaps="nodes,passage",
    )

    village = orm.relationship("Building", uselist=False, viewonly=True)

    __table_args__ = (
        sa.UniqueConstraint("village_id", "order_index", "subject", name="uq_passage_village_order"),
        sa.Index("ix_passage_village_order", "village_id", "order_index"),
    )
