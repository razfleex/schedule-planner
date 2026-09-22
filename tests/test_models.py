import unittest
from datetime import time

from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class ModelTests(unittest.TestCase):
    """Проверяет базовые правила моделей предметной области."""

    def setUp(self) -> None:
        """Создаёт исходные сущности для тестов занятия."""
        self.teacher = Teacher(1, "Иванов И. И.")
        self.group = Group(1, "ИВТ-261")
        self.subject = Subject(1, "Программная инженерия")
        self.classroom = Classroom(1, "Б-305")

    def test_lesson_with_valid_time_is_created(self) -> None:
        """Проверяет создание занятия с корректным интервалом времени."""
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

        self.assertEqual(lesson.teacher, self.teacher)
        self.assertEqual(lesson.group, self.group)

    def test_lesson_with_equal_times_is_rejected(self) -> None:
        """Проверяет запрет занятия с одинаковым временем начала и окончания."""
        with self.assertRaises(ValueError):
            Lesson(
                id=1,
                teacher=self.teacher,
                group=self.group,
                subject=self.subject,
                classroom=self.classroom,
                day_of_week=Weekday.MONDAY,
                start_time=time(9, 0),
                end_time=time(9, 0),
            )

    def test_lesson_with_end_before_start_is_rejected(self) -> None:
        """Проверяет запрет занятия с окончанием раньше начала."""
        with self.assertRaises(ValueError):
            Lesson(
                id=1,
                teacher=self.teacher,
                group=self.group,
                subject=self.subject,
                classroom=self.classroom,
                day_of_week=Weekday.MONDAY,
                start_time=time(10, 30),
                end_time=time(9, 0),
            )

    def test_empty_teacher_name_is_rejected(self) -> None:
        """Проверяет запрет преподавателя без ФИО."""
        with self.assertRaises(ValueError):
            Teacher(1, "   ")


if __name__ == "__main__":
    unittest.main()