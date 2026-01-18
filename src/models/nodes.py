import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.mutable import MutableDict

from src.app.database import Base


class PassageNode(Base):
    __tablename__ = "nodes"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)

    passage_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("passages.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # NULL = общая нода, NOT NULL = персональная нода конкретного юзера
    user_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    content: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)

    # boss бывает только у shared нод (user_id IS NULL)
    is_boss: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False, nullable=False)

    config: orm.Mapped[dict] = orm.mapped_column(
        MutableDict.as_mutable(sa.JSON),
        default=dict,
        nullable=False,
    )

    pass_score: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    reward_coins: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)
    reward_xp: orm.Mapped[int | None] = orm.mapped_column(sa.Integer, nullable=True)

    questions = orm.relationship("Question")

    progresses = orm.relationship("UserNodeProgress")

    __table_args__ = (
        # --- Индексы для сортировки/поиска ---
        sa.Index("ix_nodes_passage", "passage_id"),
        sa.Index("ix_nodes_passage_user", "passage_id", "user_id"),

        # --- Ограничение boss ---
        # 1) Босс не может быть персональным
        sa.CheckConstraint(
            "NOT (is_boss = true AND user_id IS NOT NULL)",
            name="ck_nodes_boss_must_be_shared",
        ),
        # 2) Ровно один shared boss на passage (PostgreSQL partial unique)
        sa.Index(
            "uq_nodes_one_shared_boss_per_passage",
            "passage_id",
            unique=True,
            postgresql_where=sa.text("is_boss = true AND user_id IS NULL"),
        ),
        # --- Валидация полей босса ---
        sa.CheckConstraint(
            "(is_boss = false) OR (pass_score IS NOT NULL AND reward_coins IS NOT NULL AND reward_xp IS NOT NULL)",
            name="ck_nodes_boss_fields_required",
        ),
    )
