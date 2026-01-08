import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.app.database import Base


class RoadmapEdge(Base):
    __tablename__ = 'roadmap_edges'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    order_index: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    user_id: orm.Mapped[int | None] = orm.mapped_column(sa.ForeignKey('users.id', ondelete="CASCADE"))
    village_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('villages.id', ondelete="CASCADE"))
    questions = orm.relationship("Question", back_populates="edge")