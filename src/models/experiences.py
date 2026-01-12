import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Experience(Base):
    __tablename__ = 'experiences'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'))

    level: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=1)

    current_xp: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)

    @property
    def capacity(self) -> int:
        from src.app.constants import LEVEL_TABLE, MAX_LEVEL
        level = self.level if self.level <= MAX_LEVEL else MAX_LEVEL
        return LEVEL_TABLE.get(level)
