from api_test_base import ApiTestBase


class TestCatalogUsageAPI(ApiTestBase):
    """Проверка связей справочных сущностей с занятиями."""

    def setUp(self) -> None:
        super().setUp()

        catalog_data = [
            ("/teachers", {"id": 1, "full_name": "Иванов"}),
            ("/groups", {"id": 1, "name": "ИВТ-21"}),
            ("/subjects", {"id": 1, "name": "Математика"}),
            ("/classrooms", {"id": 1, "name": "305"}),
        ]

        for path, data in catalog_data:
            response = self.client.post(path, json=data)
            self.assertEqual(response.status_code, 201)

        lesson_data = {
            "id": 1,
            "teacher_id": 1,
            "group_id": 1,
            "subject_id": 1,
            "classroom_id": 1,
            "day_of_week": "Понедельник",
            "start_time": "09:00:00",
            "end_time": "10:30:00",
        }

        response = self.client.post("/lessons", json=lesson_data)

        self.assertEqual(response.status_code, 201)

    def test_cannot_delete_used_teacher(self) -> None:
        response = self.client.delete("/teachers/1")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            self.client.get("/teachers/1").status_code,
            200,
        )

    def test_cannot_delete_used_group(self) -> None:
        response = self.client.delete("/groups/1")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            self.client.get("/groups/1").status_code,
            200,
        )

    def test_cannot_delete_used_subject(self) -> None:
        response = self.client.delete("/subjects/1")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            self.client.get("/subjects/1").status_code,
            200,
        )

    def test_cannot_delete_used_classroom(self) -> None:
        response = self.client.delete("/classrooms/1")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            self.client.get("/classrooms/1").status_code,
            200,
        )

    def test_delete_catalog_after_lesson_removal(self) -> None:
        response = self.client.delete("/lessons/1")

        self.assertEqual(response.status_code, 204)

        paths = [
            "/teachers/1",
            "/groups/1",
            "/subjects/1",
            "/classrooms/1",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.delete(path)

                self.assertEqual(response.status_code, 204)

    def test_update_used_catalog_entities(self) -> None:
        updates = [
            (
                "/teachers/1",
                {"id": 1, "full_name": "Петров"},
                "teacher",
            ),
            (
                "/groups/1",
                {"id": 1, "name": "ИВТ-22"},
                "group",
            ),
            (
                "/subjects/1",
                {"id": 1, "name": "Информатика"},
                "subject",
            ),
            (
                "/classrooms/1",
                {"id": 1, "name": "306"},
                "classroom",
            ),
        ]

        for path, data, field in updates:
            with self.subTest(path=path):
                response = self.client.put(path, json=data)

                self.assertEqual(response.status_code, 200)

                lesson = self.client.get("/lessons/1")

                self.assertEqual(lesson.status_code, 200)
                self.assertEqual(lesson.json()[field], data)
