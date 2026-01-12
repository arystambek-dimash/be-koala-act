from datetime import datetime, date

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class UserCastle(Base):
    __tablename__ = 'user_castles'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    castle_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('buildings.id', ondelete='CASCADE'))
    treasure_amount: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    last_collect_date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)

    # Tap system fields
    taps_used_today: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    last_tap_reset_date: orm.Mapped[date] = orm.mapped_column(sa.Date, nullable=True)

    castle = orm.relationship("Building", foreign_keys=[castle_id])
