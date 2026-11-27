from api_test_base import ApiTestBase


class TestLessonsAPI(ApiTestBase):
    """Интеграционные тесты API учебных занятий."""

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

    def create_lesson(self, data=None):
        if data is None:
            data = self.lesson_data

        response = self.client.post("/lessons", json=data)
        self.assertEqual(response.status_code, 201)

        return response.json()

    def test_get_empty_lessons(self) -> None:
        response = self.client.get("/lessons")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_lesson(self) -> None:
        lesson = self.create_lesson()

        self.assertEqual(lesson["id"], 1)
        self.assertEqual(lesson["teacher"]["id"], 1)
        self.assertEqual(lesson["group"]["id"], 1)
        self.assertEqual(lesson["subject"]["id"], 1)
        self.assertEqual(lesson["classroom"]["id"], 1)
        self.assertEqual(lesson["day_of_week"], "Понедельник")
        self.assertEqual(lesson["start_time"], "09:00:00")
        self.assertEqual(lesson["end_time"], "10:30:00")

        saved = self.client.get("/lessons/1")

        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), lesson)

    def test_get_lessons(self) -> None:
        lesson = self.create_lesson()

        response = self.client.get("/lessons")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [lesson])

    def test_get_lesson_by_id(self) -> None:
        lesson = self.create_lesson()

        response = self.client.get("/lessons/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), lesson)

    def test_update_lesson(self) -> None:
        self.create_lesson()

        updated_data = {
            **self.lesson_data,
            "start_time": "11:00:00",
            "end_time": "12:30:00",
        }

        response = self.client.put(
            "/lessons/1",
            json=updated_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["start_time"], "11:00:00")

        saved = self.client.get("/lessons/1")

        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), response.json())

    def test_delete_lesson(self) -> None:
        self.create_lesson()

        response = self.client.delete("/lessons/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            self.client.get("/lessons/1").status_code,
            404,
        )

    def test_missing_lesson(self) -> None:
        self.assertEqual(
            self.client.get("/lessons/1").status_code,
            404,
        )

        response = self.client.put(
            "/lessons/1",
            json=self.lesson_data,
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/lessons/1")
        self.assertEqual(response.status_code, 404)

    def test_duplicate_lesson(self) -> None:
        self.create_lesson()

        response = self.client.post(
            "/lessons",
            json=self.lesson_data,
        )

        self.assertEqual(response.status_code, 409)

    def test_missing_catalog_entities(self) -> None:
        fields = [
            "teacher_id",
            "group_id",
            "subject_id",
            "classroom_id",
        ]

        for field in fields:
            with self.subTest(field=field):
                data = {
                    **self.lesson_data,
                    field: 999,
                }

                response = self.client.post("/lessons", json=data)

                self.assertEqual(response.status_code, 404)

        self.assertEqual(self.client.get("/lessons").json(), [])

    def test_invalid_lesson_id(self) -> None:
        data = {**self.lesson_data, "id": -1}

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 422)

    def test_invalid_lesson_time(self) -> None:
        data = {
            **self.lesson_data,
            "end_time": "08:00:00",
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 422)

    def test_invalid_weekday(self) -> None:
        data = {
            **self.lesson_data,
            "day_of_week": "Несуществующий день",
        }

        response = self.client.post("/lessons", json=data)

        self.assertEqual(response.status_code, 422)

    def test_update_lesson_id_mismatch(self) -> None:
        self.create_lesson()

        data = {**self.lesson_data, "id": 2}

        response = self.client.put("/lessons/1", json=data)

        self.assertEqual(response.status_code, 400)

    def test_filter_lessons(self) -> None:
        self.create_lesson()

        second_lesson = {
            **self.lesson_data,
            "id": 2,
            "teacher_id": 2,
            "group_id": 2,
            "classroom_id": 2,
            "day_of_week": "Вторник",
        }

        self.create_lesson(second_lesson)

        filters = [
            {"teacher_id": 1},
            {"group_id": 1},
            {"classroom_id": 1},
            {"day_of_week": "Понедельник"},
            {"teacher_id": 1, "group_id": 1},
        ]

        for params in filters:
            with self.subTest(params=params):
                response = self.client.get(
                    "/lessons",
                    params=params,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [lesson["id"] for lesson in response.json()],
                    [1],
                )

    def test_filter_no_matches(self) -> None:
        self.create_lesson()

        response = self.client.get(
            "/lessons",
            params={"teacher_id": 999},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_filter(self) -> None:
        response = self.client.get(
            "/lessons",
            params={"teacher_id": -1},
        )

        self.assertEqual(response.status_code, 422)
