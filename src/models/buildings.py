import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.dialects import postgresql

from src.app.constants import BuildingType, SubjectEnum
from src.app.database import Base


class Building(Base):
    __tablename__ = 'buildings'

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    title: orm.Mapped[str] = orm.mapped_column(sa.String)
    svg: orm.Mapped[str] = orm.mapped_column(sa.String, nullable=True)
    treasure_capacity: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=300)
    speed_production_treasure: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=1)
    cost: orm.Mapped[int | None] = orm.mapped_column(
        sa.Integer,
        nullable=True
    )  # тут будет у замков система уровень это цена для перехода следующего
    subject: orm.Mapped[SubjectEnum] = orm.mapped_column(
        postgresql.ENUM(
            SubjectEnum,
            create_type=False,
            native_enum=True
        ),
        nullable=True
    )
    next_building_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("buildings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    next_building = orm.relationship("Building", remote_side="Building.id", uselist=False)

    type: orm.Mapped[BuildingType] = orm.mapped_column(sa.Enum(BuildingType))

    __table_args__ = (
        # Если VILLAGE -> subject обязателен
        sa.CheckConstraint(
            "(type != 'village') OR (subject IS NOT NULL)",
            name="ck_building_village_requires_subject",
        ),
        # Если CASTLE -> subject должен быть NULL (чтобы не было мусора)
        sa.CheckConstraint(
            "(type = 'village') OR (subject IS NULL)",
            name="ck_building_castle_subject_null",
        ),
        # next_building не может ссылаться на сам себя
        sa.CheckConstraint(
            "next_building_id IS NULL OR next_building_id <> id",
            name="ck_building_next_not_self",
        ),
    )
