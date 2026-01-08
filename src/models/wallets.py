import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.constants import FundType
from src.app.database import Base


class Wallet(Base):
    __tablename__ = 'wallets'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'))
    fund: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    fund_type: orm.Mapped[FundType] = orm.mapped_column(sa.Enum(FundType), default=FundType.COIN)
