from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class UserVillage(Base):
    __tablename__ = 'user_villages'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'))
    village_id = orm.mapped_column(sa.ForeignKey("buildings.id", ondelete="RESTRICT"), nullable=False)
    treasure_amount: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)
    last_collect_date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_update_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)

    village = orm.relationship("Building", foreign_keys=[village_id])

    __table_args__ = (
        sa.UniqueConstraint("user_id", "village_id", name="uq_user_village"),
        sa.Index("ix_user_villages_user", "user_id"),
    )
