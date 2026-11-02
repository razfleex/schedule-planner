from datetime import time

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_planner.database.base import Base
from schedule_planner.database.catalog_models import (
    ClassroomORM,
    GroupORM,
    SubjectORM,
    TeacherORM,
)
from schedule_planner.models import Weekday


class LessonORM(Base):
    """Представляет учебное занятие в таблице lessons."""

    __tablename__ = "lessons"

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="ck_lessons_time_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"),
        nullable=False,
    )

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="RESTRICT"),
        nullable=False,
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )

    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="RESTRICT"),
        nullable=False,
    )

    day_of_week: Mapped[Weekday] = mapped_column(
        Enum(
            Weekday,
            name="weekday",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    teacher: Mapped[TeacherORM] = relationship(
        back_populates="lessons",
    )

    group: Mapped[GroupORM] = relationship(
        back_populates="lessons",
    )

    subject: Mapped[SubjectORM] = relationship(
        back_populates="lessons",
    )

    classroom: Mapped[ClassroomORM] = relationship(
        back_populates="lessons",
    )
