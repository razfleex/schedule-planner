import unittest
from datetime import time

from schedule_planner.catalog_service import CatalogService
from schedule_planner.conflicts import LessonConflictChain
from schedule_planner.lesson_repository import InMemoryLessonRepository
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)
from schedule_planner.schedule_cli import ScheduleCli
from schedule_planner.schedule_service import ScheduleService


class CatalogUpdateIntegrationTests(unittest.TestCase):
    """Проверяет обновление справочников, связанных с занятиями."""

    def setUp(self) -> None:
        """Создаёт каталог и занятие со связанными объектами."""
        self.catalog_service = CatalogService()

        teacher = self.catalog_service.add_teacher(
            Teacher(1, "Иванов И. И.")
        )
        group = self.catalog_service.add_group(
            Group(10, "ИВТ-261")
        )
        subject = self.catalog_service.add_subject(
            Subject(20, "Математика")
        )
        classroom = self.catalog_service.add_classroom(
            Classroom(30, "101")
        )

        self.lesson_repository = InMemoryLessonRepository()
        self.lesson_repository.add(
            Lesson(
                id=100,
                teacher=teacher,
                group=group,
                subject=subject,
                classroom=classroom,
                day_of_week=Weekday.MONDAY,
                start_time=time(9, 0),
                end_time=time(10, 30),
            )
        )

    def test_updates_preserve_lesson_references(self) -> None:
        """Проверяет сохранение связей после обновления справочников."""
        self.catalog_service.update_teacher(
            Teacher(1, "Петров П. П.")
        )
        self.catalog_service.update_group(
            Group(10, "ИВТ-262")
        )
        self.catalog_service.update_subject(
            Subject(20, "Физика")
        )
        self.catalog_service.update_classroom(
            Classroom(30, "202")
        )

        lesson = self.lesson_repository.get_all()[0]

        self.assertIs(
            lesson.teacher,
            self.catalog_service.get_teacher_by_id(1),
        )
        self.assertIs(
            lesson.group,
            self.catalog_service.get_group_by_id(10),
        )
        self.assertIs(
            lesson.subject,
            self.catalog_service.get_subject_by_id(20),
        )
        self.assertIs(
            lesson.classroom,
            self.catalog_service.get_classroom_by_id(30),
        )

        self.assertEqual(lesson.teacher.full_name, "Петров П. П.")
        self.assertEqual(lesson.group.name, "ИВТ-262")
        self.assertEqual(lesson.subject.name, "Физика")
        self.assertEqual(lesson.classroom.name, "202")

    def test_updated_names_are_displayed_in_schedule(self) -> None:
        """Проверяет вывод изменённых данных в расписании."""
        self.catalog_service.update_teacher(
            Teacher(1, "Петров П. П.")
        )
        self.catalog_service.update_group(
            Group(10, "ИВТ-262")
        )
        self.catalog_service.update_subject(
            Subject(20, "Физика")
        )
        self.catalog_service.update_classroom(
            Classroom(30, "202")
        )

        schedule_service = ScheduleService(
            self.lesson_repository,
            LessonConflictChain(),
        )

        output: list[str] = []

        schedule_cli = ScheduleCli(
            schedule_service,
            output=output.append,
        )

        schedule_cli.show_all_lessons()

        self.assertIn(
            "[100] Понедельник 09:00–10:30 | "
            "ИВТ-262 | Физика | Петров П. П. | 202",
            output,
        )


if __name__ == "__main__":
    unittest.main()