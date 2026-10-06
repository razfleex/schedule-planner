import unittest
from datetime import time

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


class ScheduleCliTests(unittest.TestCase):
    """Проверяет отображение расписания в терминальном интерфейсе."""

    def setUp(self) -> None:
        """Создаёт расписание и перехватывает терминальный вывод."""
        repository = InMemoryLessonRepository()
        service = ScheduleService(
            repository,
            LessonConflictChain(),
        )

        self.teacher = Teacher(1, "Иванов И. И.")
        self.other_teacher = Teacher(2, "Петров П. П.")

        self.group = Group(1, "ИВТ-261")
        self.other_group = Group(2, "ИВТ-262")

        subject = Subject(1, "Программная инженерия")

        self.classroom = Classroom(1, "Б-305")
        self.other_classroom = Classroom(2, "Б-306")

        first_lesson = Lesson(
            id=1,
            teacher=self.teacher,
            group=self.group,
            subject=subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

        second_lesson = Lesson(
            id=2,
            teacher=self.other_teacher,
            group=self.other_group,
            subject=subject,
            classroom=self.other_classroom,
            day_of_week=Weekday.TUESDAY,
            start_time=time(11, 0),
            end_time=time(12, 30),
        )

        service.create_lesson(first_lesson)
        service.create_lesson(second_lesson)

        self.output: list[str] = []
        self.cli = ScheduleCli(service, self.output.append)

    def test_show_all_lessons(self) -> None:
        """Проверяет отображение полного расписания."""
        self.cli.show_all_lessons()

        text = "\n".join(self.output)

        self.assertIn("Полное расписание", text)
        self.assertIn("ИВТ-261", text)
        self.assertIn("ИВТ-262", text)

    def test_student_sees_only_own_group(self) -> None:
        """Проверяет расписание Студента."""
        self.cli.show_student_schedule(self.group.id)

        text = "\n".join(self.output)

        self.assertIn("ИВТ-261", text)
        self.assertNotIn("ИВТ-262", text)

    def test_teacher_sees_only_own_lessons(self) -> None:
        """Проверяет расписание Преподавателя."""
        self.cli.show_teacher_schedule(self.teacher.id)

        text = "\n".join(self.output)

        self.assertIn("Иванов И. И.", text)
        self.assertNotIn("Петров П. П.", text)

    def test_filter_by_day(self) -> None:
        """Проверяет отображение расписания выбранного дня."""
        self.cli.show_lessons_by_day(Weekday.TUESDAY)

        text = "\n".join(self.output)

        self.assertIn("Вторник", text)
        self.assertIn("ИВТ-262", text)
        self.assertNotIn("ИВТ-261", text)

    def test_empty_schedule_message(self) -> None:
        """Проверяет сообщение при отсутствии найденных занятий."""
        self.cli.show_lessons_by_group(999)

        self.assertEqual(
            self.output,
            [
                "Расписание учебной группы",
                "Занятий нет.",
            ],
        )


if __name__ == "__main__":
    unittest.main()