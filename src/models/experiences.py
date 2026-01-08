import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class Experience(Base):
    __tablename__ = 'experiences'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'))
    xp: orm.Mapped[float] = orm.mapped_column(sa.Float, default=0)
