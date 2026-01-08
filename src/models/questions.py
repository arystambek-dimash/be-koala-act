from typing import Any

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Question(Base):
    __tablename__ = 'questions'
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    edge_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("roadmap_edges.id", ondelete='CASCADE'))
    type: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    content: orm.Mapped[dict[str, Any]] = orm.mapped_column(sa.JSON, nullable=False)
    difficulty: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=1)

    edge = orm.relationship("RoadmapEdge", back_populates="questions")
