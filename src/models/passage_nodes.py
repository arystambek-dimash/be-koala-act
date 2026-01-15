import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.mutable import MutableDict

from src.app.database import Base


class PassageNode(Base):
    __tablename__ = "roadmap_nodes"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)

    passage_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("roadmap_passages.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: orm.Mapped[int | None] = orm.mapped_column(sa.ForeignKey(
        "users.id",
        ondelete="CASCADE",
    ), nullable=True, index=True)

    title: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    content: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)

    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)

    # ✅ тип ноды
    is_boss: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False, nullable=False)

    config: orm.Mapped[dict] = orm.mapped_column(
        MutableDict.as_mutable(sa.JSON),
        default=dict,
        nullable=False,
    )
    pass_score: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    reward_coins: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    reward_xp: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)

    passage = orm.relationship("Passage", back_populates="nodes")
    questions = orm.relationship("Question")
    progresses = orm.relationship("UserNodeProgress")

    __table_args__ = (
        # порядок в пределах passage
        sa.UniqueConstraint("passage_id", "order_index", name="uq_nodes_passage_order"),
        sa.Index("ix_nodes_passage_order", "passage_id", "order_index"),

        # ✅ максимум 1 boss на passage (PostgreSQL)
        sa.Index(
            "uq_nodes_one_boss_per_passage",
            "passage_id",
            unique=True,
            postgresql_where=sa.text("is_boss = true"),
        ),

        # boss -> требует pass_score/reward'ы, non-boss -> может быть null
        sa.CheckConstraint(
            "(is_boss = false) OR (pass_score IS NOT NULL AND reward_coins IS NOT NULL AND reward_xp IS NOT NULL)",
            name="ck_nodes_boss_fields_required",
        ),
    )
