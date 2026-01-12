import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.mutable import MutableDict

from src.app.database import Base


class PassageBoss(Base):
    __tablename__ = "roadmap_passage_bosses"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    passage_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("roadmap_passages.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    node_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("roadmap_nodes.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    title: orm.Mapped[str] = orm.mapped_column(sa.String, default="Boss", nullable=False)

    config: orm.Mapped[dict] = orm.mapped_column(
        MutableDict.as_mutable(sa.JSON),
        default=dict,
        nullable=False,
    )

    pass_score: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=70, nullable=False)
    reward_coins: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=50, nullable=False)
    reward_xp: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=100, nullable=False)

    passage = orm.relationship("Passage", back_populates="boss")

    node = orm.relationship(
        "PassageNode",
        foreign_keys=[node_id],
    )
