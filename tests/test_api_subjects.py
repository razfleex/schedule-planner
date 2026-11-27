from api_test_base import ApiTestBase


class TestSubjectsAPI(ApiTestBase):
    """Интеграционные тесты API учебных дисциплин."""

    def setUp(self) -> None:
        super().setUp()

        self.subject_data = {
            "id": 1,
            "name": "Математика",
        }

    def test_get_empty_subjects(self) -> None:
        response = self.client.get("/subjects")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_subject(self) -> None:
        response = self.client.post(
            "/subjects",
            json=self.subject_data,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.subject_data)

        saved = self.client.get("/subjects/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), self.subject_data)

    def test_get_subjects(self) -> None:
        created = self.client.post("/subjects", json=self.subject_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.get("/subjects")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.subject_data])

    def test_update_subject(self) -> None:
        created = self.client.post("/subjects", json=self.subject_data)
        self.assertEqual(created.status_code, 201)

        updated_data = {
            "id": 1,
            "name": "Информатика",
        }

        response = self.client.put(
            "/subjects/1",
            json=updated_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), updated_data)

        saved = self.client.get("/subjects/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), updated_data)

    def test_delete_subject(self) -> None:
        created = self.client.post("/subjects", json=self.subject_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.delete("/subjects/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            self.client.get("/subjects/1").status_code,
            404,
        )

    def test_missing_subject(self) -> None:
        response = self.client.get("/subjects/1")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/subjects/1",
            json=self.subject_data,
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/subjects/1")
        self.assertEqual(response.status_code, 404)

    def test_duplicate_subject(self) -> None:
        created = self.client.post("/subjects", json=self.subject_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.post(
            "/subjects",
            json=self.subject_data,
        )

        self.assertEqual(response.status_code, 409)

    def test_invalid_subject_name(self) -> None:
        response = self.client.post(
            "/subjects",
            json={"id": 1, "name": ""},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_subject_id(self) -> None:
        response = self.client.post(
            "/subjects",
            json={"id": -1, "name": "Математика"},
        )

        self.assertEqual(response.status_code, 422)

    def test_update_subject_id_mismatch(self) -> None:
        created = self.client.post("/subjects", json=self.subject_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.put(
            "/subjects/1",
            json={"id": 2, "name": "Информатика"},
        )

        self.assertEqual(response.status_code, 400)
