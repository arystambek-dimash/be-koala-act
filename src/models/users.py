from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class User(Base):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    email: orm.Mapped[str] = orm.mapped_column(sa.String, unique=True)
    full_name: orm.Mapped[str] = orm.mapped_column(sa.String)
    current_score: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    target_score: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=36)
    exam_date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime)
    has_onboard: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)
