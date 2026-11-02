from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from schedule_planner.database.base import Base

if TYPE_CHECKING:
    from schedule_planner.database.lesson_model import LessonORM


class TeacherORM(Base):
    """Хранит сведения о преподавателях в таблице teachers."""

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    full_name: Mapped[str] = mapped_column(
        nullable=False,
    )

    lessons: Mapped[list[LessonORM]] = relationship(
        "LessonORM",
        back_populates="teacher",
        passive_deletes="all",
    )


class GroupORM(Base):
    """Хранит сведения об учебных группах в таблице groups."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
    )

    lessons: Mapped[list[LessonORM]] = relationship(
        "LessonORM",
        back_populates="group",
        passive_deletes="all",
    )

    subjects: Mapped[list[SubjectORM]] = relationship(
        "SubjectORM",
        secondary="lessons",
        back_populates="groups",
        viewonly=True,
    )


class SubjectORM(Base):
    """Хранит сведения о дисциплинах в таблице subjects."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
    )

    lessons: Mapped[list[LessonORM]] = relationship(
        "LessonORM",
        back_populates="subject",
        passive_deletes="all",
    )

    groups: Mapped[list[GroupORM]] = relationship(
        "GroupORM",
        secondary="lessons",
        back_populates="subjects",
        viewonly=True,
    )


class ClassroomORM(Base):
    """Хранит сведения об аудиториях в таблице classrooms."""

    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
    )

    lessons: Mapped[list[LessonORM]] = relationship(
        "LessonORM",
        back_populates="classroom",
        passive_deletes="all",
    )
