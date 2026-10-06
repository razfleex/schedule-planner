import unittest
from datetime import time

from schedule_planner.catalog_repository import InMemoryRepository
from schedule_planner.catalog_service import CatalogService
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


class CatalogDeletionIntegrationTests(unittest.TestCase):
    """Проверяет защиту связанных справочных сущностей от удаления."""

    def setUp(self) -> None:
        """Создаёт связанные каталоги, занятие и сервис."""
        self.teacher = Teacher(1, "Иванов И. И.")
        self.group = Group(1, "ИВТ-261")
        self.subject = Subject(1, "Программная инженерия")
        self.classroom = Classroom(1, "Б-305")

        self.teacher_repo = InMemoryRepository[Teacher]()
        self.group_repo = InMemoryRepository[Group]()
        self.subject_repo = InMemoryRepository[Subject]()
        self.classroom_repo = InMemoryRepository[Classroom]()

        self.teacher_repo.add(self.teacher)
        self.group_repo.add(self.group)
        self.subject_repo.add(self.subject)
        self.classroom_repo.add(self.classroom)

        self.lesson_repository = InMemoryLessonRepository()
        self.lesson_repository.add(
            Lesson(
                id=1,
                teacher=self.teacher,
                group=self.group,
                subject=self.subject,
                classroom=self.classroom,
                day_of_week=Weekday.MONDAY,
                start_time=time(9, 0),
                end_time=time(10, 30),
            )
        )

        self.service = CatalogService(
            teacher_repo=self.teacher_repo,
            group_repo=self.group_repo,
            subject_repo=self.subject_repo,
            classroom_repo=self.classroom_repo,
            usage_checker=CatalogUsageChecker(self.lesson_repository),
        )

    def test_used_teacher_cannot_be_deleted(self) -> None:
        """Проверяет запрет удаления преподавателя из существующего занятия."""
        with self.assertRaises(CatalogEntityInUseError):
            self.service.delete_teacher(1)

        self.assertEqual(self.service.get_teacher_by_id(1), self.teacher)

    def test_used_group_cannot_be_deleted(self) -> None:
        """Проверяет запрет удаления группы из существующего занятия."""
        with self.assertRaises(CatalogEntityInUseError):
            self.service.delete_group(1)

        self.assertEqual(self.service.get_group_by_id(1), self.group)

    def test_used_subject_cannot_be_deleted(self) -> None:
        """Проверяет запрет удаления дисциплины из существующего занятия."""
        with self.assertRaises(CatalogEntityInUseError):
            self.service.delete_subject(1)

        self.assertEqual(self.service.get_subject_by_id(1), self.subject)

    def test_used_classroom_cannot_be_deleted(self) -> None:
        """Проверяет запрет удаления аудитории из существующего занятия."""
        with self.assertRaises(CatalogEntityInUseError):
            self.service.delete_classroom(1)

        self.assertEqual(
            self.service.get_classroom_by_id(1),
            self.classroom,
        )

    def test_entity_can_be_deleted_after_lesson_removal(self) -> None:
        """Проверяет удаление сущности после удаления связанного занятия."""
        self.lesson_repository.delete(1)

        self.service.delete_teacher(1)

        self.assertIsNone(self.service.get_teacher_by_id(1))


if __name__ == "__main__":
    unittest.main()