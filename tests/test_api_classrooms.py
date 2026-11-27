from api_test_base import ApiTestBase


class TestClassroomsAPI(ApiTestBase):
    """Интеграционные тесты API аудиторий."""

    def setUp(self) -> None:
        super().setUp()

        self.classroom_data = {
            "id": 1,
            "name": "305",
        }

    def test_get_empty_classrooms(self) -> None:
        response = self.client.get("/classrooms")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_classroom(self) -> None:
        response = self.client.post(
            "/classrooms",
            json=self.classroom_data,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.classroom_data)

        saved = self.client.get("/classrooms/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), self.classroom_data)

    def test_get_classrooms(self) -> None:
        created = self.client.post("/classrooms", json=self.classroom_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.get("/classrooms")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.classroom_data])

    def test_update_classroom(self) -> None:
        created = self.client.post("/classrooms", json=self.classroom_data)
        self.assertEqual(created.status_code, 201)

        updated_data = {
            "id": 1,
            "name": "306",
        }

        response = self.client.put(
            "/classrooms/1",
            json=updated_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), updated_data)

        saved = self.client.get("/classrooms/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), updated_data)

    def test_delete_classroom(self) -> None:
        created = self.client.post("/classrooms", json=self.classroom_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.delete("/classrooms/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            self.client.get("/classrooms/1").status_code,
            404,
        )

    def test_missing_classroom(self) -> None:
        response = self.client.get("/classrooms/1")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/classrooms/1",
            json=self.classroom_data,
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/classrooms/1")
        self.assertEqual(response.status_code, 404)

    def test_duplicate_classroom(self) -> None:
        created = self.client.post("/classrooms", json=self.classroom_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.post(
            "/classrooms",
            json=self.classroom_data,
        )

        self.assertEqual(response.status_code, 409)

    def test_invalid_classroom_name(self) -> None:
        response = self.client.post(
            "/classrooms",
            json={"id": 1, "name": ""},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_classroom_id(self) -> None:
        response = self.client.post(
            "/classrooms",
            json={"id": -1, "name": "305"},
        )

        self.assertEqual(response.status_code, 422)

    def test_update_classroom_id_mismatch(self) -> None:
        created = self.client.post("/classrooms", json=self.classroom_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.put(
            "/classrooms/1",
            json={"id": 2, "name": "306"},
        )

        self.assertEqual(response.status_code, 400)
