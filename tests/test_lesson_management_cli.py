import unittest
from datetime import time

from schedule_planner.catalog_service import CatalogService
from schedule_planner.conflicts import LessonConflictChain
from schedule_planner.lesson_management_cli import LessonManagementCli
from schedule_planner.lesson_repository import InMemoryLessonRepository
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)
from schedule_planner.schedule_service import ScheduleService


class LessonManagementCliTests(unittest.TestCase):
    """Проверяет управление занятиями через терминальный интерфейс."""

    def setUp(self) -> None:
        """Создаёт сервисы и тестовые справочные сущности."""
        self.lesson_repository = InMemoryLessonRepository()
        self.schedule_service = ScheduleService(
            self.lesson_repository,
            LessonConflictChain(),
        )

        self.catalog_service = CatalogService()

        self.teacher = Teacher(1, "Иванов И. И.")
        self.group = Group(1, "ИВТ-261")
        self.subject = Subject(1, "Программная инженерия")
        self.classroom = Classroom(1, "Б-305")

        self.catalog_service.add_teacher(self.teacher)
        self.catalog_service.add_group(self.group)
        self.catalog_service.add_subject(self.subject)
        self.catalog_service.add_classroom(self.classroom)

        self.output: list[str] = []

    def make_cli(self, answers: list[str]) -> LessonManagementCli:
        """Создаёт CLI с заранее подготовленными ответами пользователя."""
        answer_iterator = iter(answers)

        return LessonManagementCli(
            schedule_service=self.schedule_service,
            catalog_service=self.catalog_service,
            input_func=lambda _: next(answer_iterator),
            output=self.output.append,
        )

    def add_existing_lesson(self) -> Lesson:
        """Добавляет занятие в расписание для тестов."""
        lesson = Lesson(
            id=1,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

        self.schedule_service.create_lesson(lesson)
        return lesson

    def test_create_lesson(self) -> None:
        """Проверяет создание занятия через CLI."""
        cli = self.make_cli(
            [
                "1",
                "1",
                "1",
                "1",
                "1",
                "1",
                "09:00",
                "10:30",
            ]
        )

        cli.create_lesson()

        lesson = self.schedule_service.get_lesson(1)

        self.assertIsNotNone(lesson)
        self.assertIn("Занятие 1 создано.", self.output)

    def test_update_lesson(self) -> None:
        """Проверяет изменение занятия через CLI."""
        self.add_existing_lesson()

        cli = self.make_cli(
            [
                "1",
                "1",
                "1",
                "1",
                "1",
                "2",
                "11:00",
                "12:30",
            ]
        )

        cli.update_lesson()

        lesson = self.schedule_service.get_lesson(1)

        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.day_of_week, Weekday.TUESDAY)
        self.assertEqual(lesson.start_time, time(11, 0))
        self.assertIn("Занятие 1 изменено.", self.output)

    def test_delete_lesson(self) -> None:
        """Проверяет удаление занятия через CLI."""
        self.add_existing_lesson()

        cli = self.make_cli(["1"])

        cli.delete_lesson()

        self.assertIsNone(self.schedule_service.get_lesson(1))
        self.assertIn("Занятие 1 удалено.", self.output)

    def test_unknown_teacher_is_rejected(self) -> None:
        """Проверяет ошибку при неизвестном преподавателе."""
        cli = self.make_cli(
            [
                "1",
                "999",
            ]
        )

        cli.create_lesson()

        self.assertIsNone(self.schedule_service.get_lesson(1))
        self.assertIn(
            "Ошибка: Преподаватель с идентификатором 999 не найден.",
            self.output,
        )

    def test_conflicting_lesson_is_rejected(self) -> None:
        """Проверяет вывод ошибки при временном конфликте."""
        self.add_existing_lesson()

        cli = self.make_cli(
            [
                "2",
                "1",
                "1",
                "1",
                "1",
                "1",
                "10:00",
                "11:30",
            ]
        )

        cli.create_lesson()

        self.assertIsNone(self.schedule_service.get_lesson(2))
        self.assertTrue(
            any(message.startswith("Ошибка:") for message in self.output)
        )


if __name__ == "__main__":
    unittest.main()