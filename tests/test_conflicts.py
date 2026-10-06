import unittest
from datetime import time

from schedule_planner.conflicts import (
    LessonConflictChain,
    ScheduleConflictError,
)
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class ConflictTests(unittest.TestCase):
    """Проверяет правила временных конфликтов расписания."""

    def setUp(self) -> None:
        """Создаёт исходные сущности и проверяющий объект."""
        self.checker = LessonConflictChain()

        self.teacher = Teacher(1, "Иванов И. И.")
        self.other_teacher = Teacher(2, "Петров П. П.")

        self.group = Group(1, "ИВТ-261")
        self.other_group = Group(2, "ИВТ-262")

        self.subject = Subject(1, "Программная инженерия")

        self.classroom = Classroom(1, "Б-305")
        self.other_classroom = Classroom(2, "Б-306")

        self.existing_lesson = Lesson(
            id=1,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

    def test_teacher_conflict_is_rejected(self) -> None:
        """Проверяет обнаружение занятого преподавателя."""
        lesson = Lesson(
            id=2,
            teacher=self.teacher,
            group=self.other_group,
            subject=self.subject,
            classroom=self.other_classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 30),
        )

        with self.assertRaisesRegex(
            ScheduleConflictError,
            "Конфликт преподавателя",
        ):
            self.checker.check(lesson, [self.existing_lesson])

    def test_group_conflict_is_rejected(self) -> None:
        """Проверяет обнаружение занятой учебной группы."""
        lesson = Lesson(
            id=2,
            teacher=self.other_teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.other_classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 30),
        )

        with self.assertRaisesRegex(
            ScheduleConflictError,
            "Конфликт учебной группы",
        ):
            self.checker.check(lesson, [self.existing_lesson])

    def test_classroom_conflict_is_rejected(self) -> None:
        """Проверяет обнаружение занятой аудитории."""
        lesson = Lesson(
            id=2,
            teacher=self.other_teacher,
            group=self.other_group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 30),
        )

        with self.assertRaisesRegex(
            ScheduleConflictError,
            "Конфликт аудитории",
        ):
            self.checker.check(lesson, [self.existing_lesson])

    def test_touching_intervals_are_allowed(self) -> None:
        """Проверяет допустимость соседних временных интервалов."""
        lesson = Lesson(
            id=2,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(10, 30),
            end_time=time(12, 0),
        )

        self.checker.check(lesson, [self.existing_lesson])

    def test_same_time_on_different_day_is_allowed(self) -> None:
        """Проверяет отсутствие конфликта в разные дни недели."""
        lesson = Lesson(
            id=2,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.TUESDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

        self.checker.check(lesson, [self.existing_lesson])

    def test_unrelated_overlapping_lessons_are_allowed(self) -> None:
        """Проверяет пересечение независимых занятий."""
        lesson = Lesson(
            id=2,
            teacher=self.other_teacher,
            group=self.other_group,
            subject=self.subject,
            classroom=self.other_classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 30),
        )

        self.checker.check(lesson, [self.existing_lesson])


if __name__ == "__main__":
    unittest.main()