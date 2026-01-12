from typing import Any

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Question(Base):
    __tablename__ = 'questions'
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    node_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("roadmap_nodes.id", ondelete='CASCADE'),
        index=True,
    )
    type: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    content: orm.Mapped[dict[str, Any]] = orm.mapped_column(sa.JSON, nullable=False)
