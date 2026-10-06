import unittest
from datetime import time

from schedule_planner.catalog_usage_checker import (
    CatalogEntityInUseError,
    CatalogUsageChecker,
)
from schedule_planner.lesson_repository import InMemoryLessonRepository
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class CatalogUsageCheckerTests(unittest.TestCase):
    """Проверяет использование справочных сущностей в занятиях."""

    def setUp(self) -> None:
        """Создаёт хранилище с одним учебным занятием."""
        self.repository = InMemoryLessonRepository()

        lesson = Lesson(
            id=1,
            teacher=Teacher(1, "Иванов И. И."),
            group=Group(1, "ИВТ-261"),
            subject=Subject(1, "Программная инженерия"),
            classroom=Classroom(1, "Б-305"),
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

        self.repository.add(lesson)
        self.checker = CatalogUsageChecker(self.repository)

    def test_used_teacher_is_rejected(self) -> None:
        """Проверяет обнаружение используемого преподавателя."""
        with self.assertRaises(CatalogEntityInUseError):
            self.checker.ensure_teacher_not_used(1)

    def test_used_group_is_rejected(self) -> None:
        """Проверяет обнаружение используемой группы."""
        with self.assertRaises(CatalogEntityInUseError):
            self.checker.ensure_group_not_used(1)

    def test_used_subject_is_rejected(self) -> None:
        """Проверяет обнаружение используемой дисциплины."""
        with self.assertRaises(CatalogEntityInUseError):
            self.checker.ensure_subject_not_used(1)

    def test_used_classroom_is_rejected(self) -> None:
        """Проверяет обнаружение используемой аудитории."""
        with self.assertRaises(CatalogEntityInUseError):
            self.checker.ensure_classroom_not_used(1)

    def test_unused_entities_are_allowed(self) -> None:
        """Проверяет отсутствие ошибки для неиспользуемых сущностей."""
        self.checker.ensure_teacher_not_used(999)
        self.checker.ensure_group_not_used(999)
        self.checker.ensure_subject_not_used(999)
        self.checker.ensure_classroom_not_used(999)


if __name__ == "__main__":
    unittest.main()