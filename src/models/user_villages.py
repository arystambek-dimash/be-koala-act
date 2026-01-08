from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.constants import SubjectEnum
from src.app.database import Base


class UserCastle(Base):
    __tablename__ = 'user_castles'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'))
    village_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('villages.id', ondelete='CASCADE'))
    treasure_amount: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    last_collect_date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_update_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)
    subject: orm.Mapped[SubjectEnum] = orm.mapped_column(sa.Enum(SubjectEnum), nullable=True)
