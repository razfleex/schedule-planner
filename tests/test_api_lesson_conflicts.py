from api_test_base import ApiTestBase


class TestLessonConflictsAPI(ApiTestBase):
    """Проверка конфликтов учебного расписания через API."""

    def setUp(self) -> None:
        super().setUp()

        catalog_data = [
            ("/teachers", {"id": 1, "full_name": "Иванов"}),
            ("/teachers", {"id": 2, "full_name": "Петров"}),
            ("/groups", {"id": 1, "name": "ИВТ-21"}),
            ("/groups", {"id": 2, "name": "ИВТ-22"}),
            ("/subjects", {"id": 1, "name": "Математика"}),
            ("/classrooms", {"id": 1, "name": "305"}),
            ("/classrooms", {"id": 2, "name": "306"}),
        ]

        for path, data in catalog_data:
            response = self.client.post(path, json=data)
            self.assertEqual(response.status_code, 201)

        self.lesson_data = {
            "id": 1,
            "teacher_id": 1,
            "group_id": 1,
            "subject_id": 1,
            "classroom_id": 1,
            "day_of_week": "Понедельник",
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post(
            "/lessons",
            json=self.lesson_data,
        )

        self.assertEqual(response.status_code, 201)

        self.second_lesson = {
            **self.lesson_data,
            "id": 2,
            "teacher_id": 2,
            "group_id": 2,
            "classroom_id": 2,
            "start_time": "10:00:00",
            "end_time": "11:30:00",
        }

    def test_teacher_conflict(self) -> None:
        data = {
            **self.second_lesson,
            "teacher_id": 1,
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 409)

    def test_group_conflict(self) -> None:
        data = {
            **self.second_lesson,
            "group_id": 1,
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 409)

    def test_classroom_conflict(self) -> None:
        data = {
            **self.second_lesson,
            "classroom_id": 1,
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 409)

    def test_parallel_lessons_without_conflict(self) -> None:
        response = self.client.post(
            "/lessons",
            json=self.second_lesson,
        )

        self.assertEqual(response.status_code, 201)

    def test_adjacent_lessons_without_conflict(self) -> None:
        data = {
            **self.lesson_data,
            "id": 2,
            "start_time": "10:30:00",
            "end_time": "12:00:00",
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 201)

    def test_different_days_without_conflict(self) -> None:
        data = {
            **self.lesson_data,
            "id": 2,
            "day_of_week": "Вторник",
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 201)

    def test_update_without_self_conflict(self) -> None:
        response = self.client.put(
            "/lessons/1",
            json=self.lesson_data,
        )

        self.assertEqual(response.status_code, 200)

    def test_update_with_conflict(self) -> None:
        created = self.client.post(
            "/lessons",
            json=self.second_lesson,
        )

        self.assertEqual(created.status_code, 201)

        original = self.client.get("/lessons/2").json()

        updated_data = {
            **self.second_lesson,
            "teacher_id": 1,
        }

        response = self.client.put(
            "/lessons/2",
            json=updated_data,
        )

        self.assertEqual(response.status_code, 409)

        saved = self.client.get("/lessons/2")

        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), original)

    def test_conflicting_lesson_not_saved(self) -> None:
        data = {
            **self.lesson_data,
            "id": 2,
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 409)

        saved = self.client.get("/lessons/2")

        self.assertEqual(saved.status_code, 404)

        lessons = self.client.get("/lessons")

        self.assertEqual(len(lessons.json()), 1)
