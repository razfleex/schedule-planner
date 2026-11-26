import unittest
from datetime import time

from pydantic import ValidationError

from schedule_planner.dtos.responses import (
    ClassroomResponse,
    GroupResponse,
    LessonResponse,
    SubjectResponse,
    TeacherResponse,
)
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class TestResponseDTOs(unittest.TestCase):
    """Тесты выходящих Pydantic DTO."""

    def setUp(self) -> None:
        self.teacher = Teacher(1, "Иванов")
        self.group = Group(2, "ИВТ-21")
        self.subject = Subject(3, "Математика")
        self.classroom = Classroom(4, "305")

        self.lesson = Lesson(
            id=1,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

    def test_teacher_response(self) -> None:
        response = TeacherResponse.model_validate(self.teacher)

        self.assertEqual(response.id, 1)
        self.assertEqual(response.full_name, "Иванов")

    def test_group_response(self) -> None:
        response = GroupResponse.model_validate(self.group)

        self.assertEqual(response.id, 2)
        self.assertEqual(response.name, "ИВТ-21")

    def test_subject_response(self) -> None:
        response = SubjectResponse.model_validate(self.subject)

        self.assertEqual(response.id, 3)
        self.assertEqual(response.name, "Математика")

    def test_classroom_response(self) -> None:
        response = ClassroomResponse.model_validate(self.classroom)

        self.assertEqual(response.id, 4)
        self.assertEqual(response.name, "305")

    def test_lesson_response(self) -> None:
        response = LessonResponse.model_validate(self.lesson)

        self.assertEqual(response.id, 1)
        self.assertEqual(response.day_of_week, Weekday.MONDAY)
        self.assertEqual(response.start_time, time(9, 0))
        self.assertEqual(response.end_time, time(10, 30))

    def test_lesson_nested_models(self) -> None:
        response = LessonResponse.model_validate(self.lesson)

        self.assertIsInstance(response.teacher, TeacherResponse)
        self.assertIsInstance(response.group, GroupResponse)
        self.assertIsInstance(response.subject, SubjectResponse)
        self.assertIsInstance(response.classroom, ClassroomResponse)

        self.assertEqual(response.teacher.id, 1)
        self.assertEqual(response.group.id, 2)
        self.assertEqual(response.subject.id, 3)
        self.assertEqual(response.classroom.id, 4)

    def test_teacher_response_serialization(self) -> None:
        response = TeacherResponse.model_validate(self.teacher)

        self.assertEqual(
            response.model_dump(),
            {"id": 1, "full_name": "Иванов"},
        )

    def test_lesson_response_serialization(self) -> None:
        response = LessonResponse.model_validate(self.lesson)
        data = response.model_dump(mode="json")

        self.assertEqual(
            data,
            {
                "id": 1,
                "teacher": {"id": 1, "full_name": "Иванов"},
                "group": {"id": 2, "name": "ИВТ-21"},
                "subject": {"id": 3, "name": "Математика"},
                "classroom": {"id": 4, "name": "305"},
                "day_of_week": "Понедельник",
                "start_time": "09:00:00",
                "end_time": "10:30:00",
            },
        )

    def test_missing_required_field(self) -> None:
        with self.assertRaises(ValidationError):
            TeacherResponse.model_validate({"id": 1})

    def test_lesson_json_round_trip(self) -> None:
        response = LessonResponse.model_validate(self.lesson)

        json_data = response.model_dump_json()
        restored = LessonResponse.model_validate_json(json_data)

        self.assertEqual(restored, response)


if __name__ == "__main__":
    unittest.main()
