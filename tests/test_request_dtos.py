import unittest
from datetime import time

from pydantic import ValidationError

from schedule_planner.dtos.requests import (
    ClassroomRequest,
    GroupRequest,
    LessonRequest,
    SubjectRequest,
    TeacherRequest,
)
from schedule_planner.models import Weekday


class TestRequestDTOs(unittest.TestCase):
    """Тесты входящих Pydantic DTO."""

    def setUp(self) -> None:
        self.lesson_data = {
            "id": 1,
            "teacher_id": 2,
            "group_id": 3,
            "subject_id": 4,
            "classroom_id": 5,
            "day_of_week": next(iter(Weekday)),
            "start_time": "09:00",
            "end_time": "10:30",
        }

    def test_teacher_request(self) -> None:
        teacher = TeacherRequest(id=1, full_name="Иванов")
        self.assertEqual(teacher.id, 1)
        self.assertEqual(teacher.full_name, "Иванов")

    def test_group_request(self) -> None:
        group = GroupRequest(id=1, name="ИВТ-21")
        self.assertEqual(group.name, "ИВТ-21")

    def test_subject_request(self) -> None:
        subject = SubjectRequest(id=1, name="Математика")
        self.assertEqual(subject.name, "Математика")

    def test_classroom_request(self) -> None:
        classroom = ClassroomRequest(id=1, name="305")
        self.assertEqual(classroom.name, "305")

    def test_invalid_id(self) -> None:
        for invalid_id in (0, -1):
            with self.subTest(id=invalid_id), self.assertRaises(ValidationError):
                TeacherRequest(id=invalid_id, full_name="Иванов")

    def test_empty_teacher_name(self) -> None:
        with self.assertRaises(ValidationError):
            TeacherRequest(id=1, full_name="")

    def test_whitespace_name(self) -> None:
        with self.assertRaises(ValidationError):
            GroupRequest(id=1, name="   ")

    def test_name_strip_whitespace(self) -> None:
        subject = SubjectRequest(id=1, name="  Математика  ")
        self.assertEqual(subject.name, "Математика")

    def test_lesson_request(self) -> None:
        lesson = LessonRequest.model_validate(self.lesson_data)
        self.assertEqual(lesson.id, 1)
        self.assertEqual(lesson.teacher_id, 2)
        self.assertEqual(lesson.start_time, time(9, 0))
        self.assertEqual(lesson.end_time, time(10, 30))

    def test_invalid_lesson_reference(self) -> None:
        for field in (
            "teacher_id",
            "group_id",
            "subject_id",
            "classroom_id",
        ):
            with self.subTest(field=field):
                data = self.lesson_data.copy()
                data[field] = -1

                with self.assertRaises(ValidationError):
                    LessonRequest.model_validate(data)

    def test_invalid_weekday(self) -> None:
        self.lesson_data["day_of_week"] = "Invalid day"

        with self.assertRaises(ValidationError):
            LessonRequest.model_validate(self.lesson_data)

    def test_invalid_time_format(self) -> None:
        self.lesson_data["start_time"] = "25:00"

        with self.assertRaises(ValidationError):
            LessonRequest.model_validate(self.lesson_data)

    def test_end_time_before_start_time(self) -> None:
        self.lesson_data["end_time"] = "08:00"

        with self.assertRaises(ValidationError):
            LessonRequest.model_validate(self.lesson_data)

    def test_equal_start_and_end_time(self) -> None:
        self.lesson_data["end_time"] = "09:00"

        with self.assertRaises(ValidationError):
            LessonRequest.model_validate(self.lesson_data)

    def test_missing_required_field(self) -> None:
        del self.lesson_data["teacher_id"]

        with self.assertRaises(ValidationError):
            LessonRequest.model_validate(self.lesson_data)


if __name__ == "__main__":
    unittest.main()
