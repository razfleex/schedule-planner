import unittest
from datetime import time

from schedule_planner.conflicts import (
    LessonConflictChain,
    ScheduleConflictError,
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
from schedule_planner.schedule_service import ScheduleService


class ScheduleServiceTests(unittest.TestCase):
    """Проверяет операции сервиса учебного расписания."""

    def setUp(self) -> None:
        """Создаёт сервис и сущности для тестирования."""
        self.repository = InMemoryLessonRepository()
        self.service = ScheduleService(
            self.repository,
            LessonConflictChain(),
        )

        self.teacher = Teacher(1, "Иванов И. И.")
        self.other_teacher = Teacher(2, "Петров П. П.")

        self.group = Group(1, "ИВТ-261")
        self.other_group = Group(2, "ИВТ-262")

        self.subject = Subject(1, "Программная инженерия")

        self.classroom = Classroom(1, "Б-305")
        self.other_classroom = Classroom(2, "Б-306")

    def make_lesson(
        self,
        lesson_id: int,
        teacher: Teacher,
        group: Group,
        classroom: Classroom,
        day: Weekday,
        start: time,
        end: time,
    ) -> Lesson:
        """Создаёт занятие с тестовыми данными."""
        return Lesson(
            id=lesson_id,
            teacher=teacher,
            group=group,
            subject=self.subject,
            classroom=classroom,
            day_of_week=day,
            start_time=start,
            end_time=end,
        )

    def test_create_lesson(self) -> None:
        """Проверяет создание занятия."""
        lesson = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(10, 30),
        )

        self.service.create_lesson(lesson)

        self.assertEqual(self.service.get_lesson(1), lesson)

    def test_conflicting_lesson_is_not_created(self) -> None:
        """Проверяет запрет сохранения конфликтующего занятия."""
        first = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(10, 30),
        )
        second = self.make_lesson(
            2,
            self.teacher,
            self.other_group,
            self.other_classroom,
            Weekday.MONDAY,
            time(10, 0),
            time(11, 30),
        )

        self.service.create_lesson(first)

        with self.assertRaises(ScheduleConflictError):
            self.service.create_lesson(second)

        self.assertIsNone(self.service.get_lesson(2))

    def test_update_excludes_lesson_itself(self) -> None:
        """Проверяет отсутствие конфликта занятия с самим собой."""
        lesson = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(10, 30),
        )
        self.service.create_lesson(lesson)

        updated = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(11, 0),
        )

        self.service.update_lesson(updated)

        self.assertEqual(self.service.get_lesson(1), updated)

    def test_conflicting_update_is_rejected(self) -> None:
        """Проверяет запрет изменения, создающего конфликт."""
        first = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(10, 30),
        )
        second = self.make_lesson(
            2,
            self.other_teacher,
            self.other_group,
            self.other_classroom,
            Weekday.MONDAY,
            time(11, 0),
            time(12, 30),
        )

        self.service.create_lesson(first)
        self.service.create_lesson(second)

        conflicting_update = self.make_lesson(
            2,
            self.teacher,
            self.other_group,
            self.other_classroom,
            Weekday.MONDAY,
            time(10, 0),
            time(11, 30),
        )

        with self.assertRaises(ScheduleConflictError):
            self.service.update_lesson(conflicting_update)

        self.assertEqual(self.service.get_lesson(2), second)

    def test_delete_lesson(self) -> None:
        """Проверяет удаление занятия."""
        lesson = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(10, 30),
        )
        self.service.create_lesson(lesson)

        self.service.delete_lesson(1)

        self.assertIsNone(self.service.get_lesson(1))

    def test_schedule_filters(self) -> None:
        """Проверяет фильтрацию расписания."""
        first = self.make_lesson(
            1,
            self.teacher,
            self.group,
            self.classroom,
            Weekday.MONDAY,
            time(9, 0),
            time(10, 30),
        )
        second = self.make_lesson(
            2,
            self.other_teacher,
            self.other_group,
            self.other_classroom,
            Weekday.TUESDAY,
            time(11, 0),
            time(12, 30),
        )

        self.service.create_lesson(first)
        self.service.create_lesson(second)

        self.assertEqual(
            self.service.get_lessons_by_teacher(self.teacher.id),
            [first],
        )
        self.assertEqual(
            self.service.get_lessons_by_group(self.other_group.id),
            [second],
        )
        self.assertEqual(
            self.service.get_lessons_by_classroom(self.classroom.id),
            [first],
        )
        self.assertEqual(
            self.service.get_lessons_by_day(Weekday.TUESDAY),
            [second],
        )


if __name__ == "__main__":
    unittest.main()