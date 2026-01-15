from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import func

from src.app.database import Base


class UserNodeProgress(Base):
    __tablename__ = 'user_node_progresses'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    node_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey('roadmap_nodes.id', ondelete='CASCADE'),
        index=True,
    )
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    accuracy: orm.Mapped[float] = orm.mapped_column(sa.Float, default=0)
    xp: orm.Mapped[float] = orm.mapped_column(sa.Float, default=0)
    correct_answer: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)

    created_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, default=func.now())