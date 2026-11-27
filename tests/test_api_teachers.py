from api_test_base import ApiTestBase


class TestTeachersAPI(ApiTestBase):
    """Интеграционные тесты API преподавателей."""

    def setUp(self) -> None:
        super().setUp()

        self.teacher_data = {
            "id": 1,
            "full_name": "Иванов Иван Иванович",
        }

    def test_get_empty_teachers(self) -> None:
        response = self.client.get("/teachers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_teacher(self) -> None:
        response = self.client.post(
            "/teachers",
            json=self.teacher_data,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.teacher_data)

        saved = self.client.get("/teachers/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), self.teacher_data)

    def test_get_teachers(self) -> None:
        self.client.post("/teachers", json=self.teacher_data)

        response = self.client.get("/teachers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.teacher_data])

    def test_get_teacher_by_id(self) -> None:
        self.client.post("/teachers", json=self.teacher_data)

        response = self.client.get("/teachers/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.teacher_data)

    def test_update_teacher(self) -> None:
        self.client.post("/teachers", json=self.teacher_data)

        updated_data = {
            "id": 1,
            "full_name": "Петров Пётр Петрович",
        }

        response = self.client.put(
            "/teachers/1",
            json=updated_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), updated_data)

        saved = self.client.get("/teachers/1")
        self.assertEqual(saved.json(), updated_data)

    def test_delete_teacher(self) -> None:
        self.client.post("/teachers", json=self.teacher_data)

        response = self.client.delete("/teachers/1")

        self.assertEqual(response.status_code, 204)

        response = self.client.get("/teachers/1")
        self.assertEqual(response.status_code, 404)

    def test_teacher_not_found(self) -> None:
        response = self.client.get("/teachers/999")

        self.assertEqual(response.status_code, 404)

    def test_duplicate_teacher(self) -> None:
        self.client.post("/teachers", json=self.teacher_data)

        response = self.client.post(
            "/teachers",
            json=self.teacher_data,
        )

        self.assertEqual(response.status_code, 409)

    def test_invalid_teacher_name(self) -> None:
        response = self.client.post(
            "/teachers",
            json={"id": 1, "full_name": ""},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_teacher_id(self) -> None:
        response = self.client.post(
            "/teachers",
            json={"id": -1, "full_name": "Иванов"},
        )

        self.assertEqual(response.status_code, 422)

    def test_update_teacher_id_mismatch(self) -> None:
        self.client.post("/teachers", json=self.teacher_data)

        response = self.client.put(
            "/teachers/1",
            json={"id": 2, "full_name": "Петров"},
        )

        self.assertEqual(response.status_code, 400)

    def test_update_missing_teacher(self) -> None:
        response = self.client.put(
            "/teachers/1",
            json=self.teacher_data,
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_missing_teacher(self) -> None:
        response = self.client.delete("/teachers/999")

        self.assertEqual(response.status_code, 404)
