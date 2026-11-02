from __future__ import annotations

from schedule_planner.database.catalog_models import (
    ClassroomORM,
    GroupORM,
    SubjectORM,
    TeacherORM,
)
from schedule_planner.database.lesson_model import LessonORM
from schedule_planner.models import Classroom, Group, Subject, Teacher

__all__ = [
    "ClassroomMapper",
    "GroupMapper",
    "LessonORM",
    "SubjectMapper",
    "TeacherMapper",
]


class TeacherMapper:
    """Маппер для преобразования между моделью Teacher и ORM-моделью TeacherORM."""

    @staticmethod
    def to_orm(entity: Teacher) -> TeacherORM:
        """Преобразует доменную модель Teacher в TeacherORM."""
        return TeacherORM(
            id=entity.id,
            full_name=entity.full_name,
        )

    @staticmethod
    def to_domain(orm_entity: TeacherORM) -> Teacher:
        """Преобразует ORM-модель TeacherORM в доменную модель Teacher."""
        return Teacher(
            id=orm_entity.id,
            full_name=orm_entity.full_name,
        )


class GroupMapper:
    """Маппер для преобразования между моделью Group и ORM-моделью GroupORM."""

    @staticmethod
    def to_orm(entity: Group) -> GroupORM:
        """Преобразует доменную модель Group в GroupORM."""
        return GroupORM(
            id=entity.id,
            name=entity.name,
        )

    @staticmethod
    def to_domain(orm_entity: GroupORM) -> Group:
        """Преобразует ORM-модель GroupORM в доменную модель Group."""
        return Group(
            id=orm_entity.id,
            name=orm_entity.name,
        )


class SubjectMapper:
    """Маппер для преобразования между моделью Subject и ORM-моделью SubjectORM."""

    @staticmethod
    def to_orm(entity: Subject) -> SubjectORM:
        """Преобразует доменную модель Subject в SubjectORM."""
        return SubjectORM(
            id=entity.id,
            name=entity.name,
        )

    @staticmethod
    def to_domain(orm_entity: SubjectORM) -> Subject:
        """Преобразует ORM-модель SubjectORM в доменную модель Subject."""
        return Subject(
            id=orm_entity.id,
            name=orm_entity.name,
        )


class ClassroomMapper:
    """Маппер для преобразования между моделью Classroom и ORM-моделью ClassroomORM."""

    @staticmethod
    def to_orm(entity: Classroom) -> ClassroomORM:
        """Преобразует доменную модель Classroom в ClassroomORM."""
        return ClassroomORM(
            id=entity.id,
            name=entity.name,
        )

    @staticmethod
    def to_domain(orm_entity: ClassroomORM) -> Classroom:
        """Преобразует ORM-модель ClassroomORM в доменную модель Classroom."""
        return Classroom(
            id=orm_entity.id,
            name=orm_entity.name,
        )
