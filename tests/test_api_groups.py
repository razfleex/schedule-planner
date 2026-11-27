from api_test_base import ApiTestBase


class TestGroupsAPI(ApiTestBase):
    """Интеграционные тесты API учебных групп."""

    def setUp(self) -> None:
        super().setUp()

        self.group_data = {
            "id": 1,
            "name": "ИВТ-21",
        }

    def test_get_empty_groups(self) -> None:
        response = self.client.get("/groups")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_group(self) -> None:
        response = self.client.post(
            "/groups",
            json=self.group_data,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.group_data)

        saved = self.client.get("/groups/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), self.group_data)

    def test_get_groups(self) -> None:
        created = self.client.post("/groups", json=self.group_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.get("/groups")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.group_data])

    def test_update_group(self) -> None:
        created = self.client.post("/groups", json=self.group_data)
        self.assertEqual(created.status_code, 201)

        updated_data = {
            "id": 1,
            "name": "ИВТ-22",
        }

        response = self.client.put(
            "/groups/1",
            json=updated_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), updated_data)

        saved = self.client.get("/groups/1")
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json(), updated_data)

    def test_delete_group(self) -> None:
        created = self.client.post("/groups", json=self.group_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.delete("/groups/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            self.client.get("/groups/1").status_code,
            404,
        )

    def test_missing_group(self) -> None:
        response = self.client.get("/groups/1")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/groups/1",
            json=self.group_data,
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/groups/1")
        self.assertEqual(response.status_code, 404)

    def test_duplicate_group(self) -> None:
        created = self.client.post("/groups", json=self.group_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.post(
            "/groups",
            json=self.group_data,
        )

        self.assertEqual(response.status_code, 409)

    def test_invalid_group_name(self) -> None:
        response = self.client.post(
            "/groups",
            json={"id": 1, "name": ""},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_group_id(self) -> None:
        response = self.client.post(
            "/groups",
            json={"id": -1, "name": "ИВТ-21"},
        )

        self.assertEqual(response.status_code, 422)

    def test_update_group_id_mismatch(self) -> None:
        created = self.client.post("/groups", json=self.group_data)
        self.assertEqual(created.status_code, 201)

        response = self.client.put(
            "/groups/1",
            json={"id": 2, "name": "ИВТ-22"},
        )

        self.assertEqual(response.status_code, 400)
