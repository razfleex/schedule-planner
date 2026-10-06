import unittest
from datetime import time

from schedule_planner.lesson_repository import InMemoryLessonRepository
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class LessonRepositoryTests(unittest.TestCase):
    """Проверяет InMemory-хранилище учебных занятий."""

    def setUp(self) -> None:
        """Создаёт хранилище и тестовое занятие."""
        self.repository = InMemoryLessonRepository()

        self.lesson = Lesson(
            id=1,
            teacher=Teacher(1, "Иванов И. И."),
            group=Group(1, "ИВТ-261"),
            subject=Subject(1, "Программная инженерия"),
            classroom=Classroom(1, "Б-305"),
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

    def test_add_and_get_lesson(self) -> None:
        """Проверяет добавление и получение занятия."""
        self.repository.add(self.lesson)

        saved_lesson = self.repository.get_by_id(1)

        self.assertEqual(saved_lesson, self.lesson)

    def test_duplicate_id_is_rejected(self) -> None:
        """Проверяет запрет одинаковых идентификаторов занятий."""
        self.repository.add(self.lesson)

        with self.assertRaises(ValueError):
            self.repository.add(self.lesson)

    def test_update_lesson(self) -> None:
        """Проверяет изменение существующего занятия."""
        self.repository.add(self.lesson)

        updated_lesson = Lesson(
            id=1,
            teacher=self.lesson.teacher,
            group=self.lesson.group,
            subject=self.lesson.subject,
            classroom=self.lesson.classroom,
            day_of_week=Weekday.TUESDAY,
            start_time=time(11, 0),
            end_time=time(12, 30),
        )

        self.repository.update(updated_lesson)

        self.assertEqual(self.repository.get_by_id(1), updated_lesson)

    def test_delete_lesson(self) -> None:
        """Проверяет удаление существующего занятия."""
        self.repository.add(self.lesson)

        self.repository.delete(1)

        self.assertIsNone(self.repository.get_by_id(1))

    def test_get_all_lessons(self) -> None:
        """Проверяет получение всех занятий."""
        self.repository.add(self.lesson)

        lessons = self.repository.get_all()

        self.assertEqual(lessons, [self.lesson])


if __name__ == "__main__":
    unittest.main()