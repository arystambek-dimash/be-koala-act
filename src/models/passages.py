import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Passage(Base):
    __tablename__ = "passages"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)

    village_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("buildings.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    title: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)

    nodes = orm.relationship(
        "PassageNode",
        primaryjoin=(
            "and_("
            "Passage.id==PassageNode.passage_id, "
            "PassageNode.is_boss==False, "
            "PassageNode.user_id==None"
            ")"
        ),
        order_by="PassageNode.id.asc()",
        viewonly=True,
        overlaps="boss,passage",
    )

    boss = orm.relationship(
        "PassageNode",
        primaryjoin=(
            "and_("
            "Passage.id==PassageNode.passage_id, "
            "PassageNode.is_boss==True, "
            "PassageNode.user_id==None"
            ")"
        ),
        uselist=False,
        viewonly=True,
        overlaps="nodes,passage",
    )

    village = orm.relationship("Building", foreign_keys=[village_id])