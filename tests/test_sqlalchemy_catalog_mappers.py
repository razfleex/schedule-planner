from __future__ import annotations

import unittest

from schedule_planner.database.catalog_mappers import (
    ClassroomMapper,
    GroupMapper,
    SubjectMapper,
    TeacherMapper,
)
from schedule_planner.database.catalog_models import (
    ClassroomORM,
    GroupORM,
    SubjectORM,
    TeacherORM,
)
from schedule_planner.models import Classroom, Group, Subject, Teacher


class TestSqlAlchemyCatalogMappers(unittest.TestCase):
    """Тесты преобразования между dataclass-моделями и ORM-моделями."""

    def test_teacher_mapper_to_orm_and_to_domain(self) -> None:
        """Проверяет корректность прямого и обратного маппинга Teacher."""
        teacher = Teacher(id=1, full_name="Иванов Иван Иванович")
        orm_teacher = TeacherMapper.to_orm(teacher)

        self.assertIsInstance(orm_teacher, TeacherORM)
        self.assertEqual(orm_teacher.id, 1)
        self.assertEqual(orm_teacher.full_name, "Иванов Иван Иванович")

        domain_teacher = TeacherMapper.to_domain(orm_teacher)
        self.assertIsInstance(domain_teacher, Teacher)
        self.assertEqual(domain_teacher.id, 1)
        self.assertEqual(domain_teacher.full_name, "Иванов Иван Иванович")
        self.assertEqual(domain_teacher, teacher)

    def test_group_mapper_to_orm_and_to_domain(self) -> None:
        """Проверяет корректность прямого и обратного маппинга Group."""
        group = Group(id=2, name="ИВТ-261")
        orm_group = GroupMapper.to_orm(group)

        self.assertIsInstance(orm_group, GroupORM)
        self.assertEqual(orm_group.id, 2)
        self.assertEqual(orm_group.name, "ИВТ-261")

        domain_group = GroupMapper.to_domain(orm_group)
        self.assertIsInstance(domain_group, Group)
        self.assertEqual(domain_group.id, 2)
        self.assertEqual(domain_group.name, "ИВТ-261")
        self.assertEqual(domain_group, group)

    def test_subject_mapper_to_orm_and_to_domain(self) -> None:
        """Проверяет корректность прямого и обратного маппинга Subject."""
        subject = Subject(id=3, name="Программная инженерия")
        orm_subject = SubjectMapper.to_orm(subject)

        self.assertIsInstance(orm_subject, SubjectORM)
        self.assertEqual(orm_subject.id, 3)
        self.assertEqual(orm_subject.name, "Программная инженерия")

        domain_subject = SubjectMapper.to_domain(orm_subject)
        self.assertIsInstance(domain_subject, Subject)
        self.assertEqual(domain_subject.id, 3)
        self.assertEqual(domain_subject.name, "Программная инженерия")
        self.assertEqual(domain_subject, subject)

    def test_classroom_mapper_to_orm_and_to_domain(self) -> None:
        """Проверяет корректность прямого и обратного маппинга Classroom."""
        classroom = Classroom(id=4, name="А-101")
        orm_classroom = ClassroomMapper.to_orm(classroom)

        self.assertIsInstance(orm_classroom, ClassroomORM)
        self.assertEqual(orm_classroom.id, 4)
        self.assertEqual(orm_classroom.name, "А-101")

        domain_classroom = ClassroomMapper.to_domain(orm_classroom)
        self.assertIsInstance(domain_classroom, Classroom)
        self.assertEqual(domain_classroom.id, 4)
        self.assertEqual(domain_classroom.name, "А-101")
        self.assertEqual(domain_classroom, classroom)


if __name__ == "__main__":
    unittest.main()
