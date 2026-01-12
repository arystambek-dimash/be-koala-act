import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class PassageNode(Base):
    __tablename__ = "roadmap_nodes"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)

    passage_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("roadmap_passages.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    title: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    content: orm.Mapped[str | None] = orm.mapped_column(sa.Text, nullable=True)

    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)

    passage = orm.relationship("Passage", back_populates="nodes")

    __table_args__ = (
        sa.UniqueConstraint("passage_id", "order_index", name="uq_nodes_passage_order"),
        sa.Index("ix_nodes_passage_order", "passage_id", "order_index"),
    )
