import unittest
from collections.abc import Callable
from unittest.mock import patch

from schedule_planner.catalog_cli import CatalogCli
from schedule_planner.catalog_service import CatalogService


class TestCatalogCli(unittest.TestCase):
    """Проверяет управление справочниками через терминальный интерфейс."""

    def setUp(self) -> None:
        """Создаёт отдельный сервис и список сообщений перед каждым тестом."""
        self.service = CatalogService()
        self.output_logs: list[str] = []

    def _make_input(self, values: list[str]) -> Callable[[str], str]:
        """Возвращает функцию ввода с заранее подготовленными ответами."""
        answers = iter(values)
        return lambda _: next(answers)

    def _make_cli(self, values: list[str]) -> CatalogCli:
        """Создаёт CLI с подготовленными ответами и перехватом вывода."""
        return CatalogCli(
            self.service,
            input_func=self._make_input(values),
            output=self.output_logs.append,
        )

    def test_teacher_workflow(self) -> None:
        """Проверяет добавление, просмотр, изменение и удаление преподавателя."""
        self._make_cli(["1", "Иван Иванов"]).add_teacher()
        self.assertIn("Преподаватель 1 добавлен.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_teachers()
        self.assertIn("[1] Иван Иванов", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["1", "Пётр Петров"]).update_teacher()
        self.assertIn("Преподаватель 1 изменён.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_teachers()
        self.assertIn("[1] Пётр Петров", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["1"]).delete_teacher()
        self.assertIn("Преподаватель 1 удалён.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_teachers()
        self.assertIn("Список пуст.", self.output_logs)

    def test_group_workflow(self) -> None:
        """Проверяет добавление, просмотр, изменение и удаление группы."""
        self._make_cli(["10", "ИВТ-261"]).add_group()
        self.assertIn("Учебная группа 10 добавлена.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_groups()
        self.assertIn("[10] ИВТ-261", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["10", "ИВТ-262"]).update_group()
        self.assertIn("Учебная группа 10 изменена.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_groups()
        self.assertIn("[10] ИВТ-262", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["10"]).delete_group()
        self.assertIn("Учебная группа 10 удалена.", self.output_logs)

    def test_subject_workflow(self) -> None:
        """Проверяет добавление, просмотр, изменение и удаление дисциплины."""
        self._make_cli(["20", "Математика"]).add_subject()
        self.assertIn("Дисциплина 20 добавлена.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_subjects()
        self.assertIn("[20] Математика", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["20", "Физика"]).update_subject()
        self.assertIn("Дисциплина 20 изменена.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_subjects()
        self.assertIn("[20] Физика", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["20"]).delete_subject()
        self.assertIn("Дисциплина 20 удалена.", self.output_logs)

    def test_classroom_workflow(self) -> None:
        """Проверяет добавление, просмотр, изменение и удаление аудитории."""
        self._make_cli(["30", "Ауд. 101"]).add_classroom()
        self.assertIn("Аудитория 30 добавлена.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_classrooms()
        self.assertIn("[30] Ауд. 101", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["30", "Ауд. 102"]).update_classroom()
        self.assertIn("Аудитория 30 изменена.", self.output_logs)

        self.output_logs.clear()
        self._make_cli([]).show_classrooms()
        self.assertIn("[30] Ауд. 102", self.output_logs)

        self.output_logs.clear()
        self._make_cli(["30"]).delete_classroom()
        self.assertIn("Аудитория 30 удалена.", self.output_logs)

    def test_invalid_id(self) -> None:
        """Проверяет понятную ошибку при вводе нецелого ID."""
        self._make_cli(["abc"]).add_teacher()
        self.assertEqual(self.output_logs, ["Ошибка: ID должен быть целым числом."])
        self.assertEqual(self.service.get_all_teachers(), [])

    def test_missing_entity(self) -> None:
        """Проверяет сообщение при удалении несуществующей сущности."""
        self._make_cli(["999"]).delete_teacher()
        self.assertEqual(len(self.output_logs), 1)
        self.assertIn("Ошибка:", self.output_logs[0])
        self.assertIn("999", self.output_logs[0])

    def test_duplicate_entity(self) -> None:
        """Проверяет сообщение при попытке повторно добавить преподавателя."""
        self._make_cli(["1", "Иван Иванов"]).add_teacher()

        self.output_logs.clear()
        self._make_cli(["1", "Пётр Петров"]).add_teacher()
        self.assertEqual(len(self.output_logs), 1)
        self.assertTrue(self.output_logs[0].startswith("Ошибка:"))
        self.assertIn("1", self.output_logs[0])

    def test_service_error_is_displayed(self) -> None:
        """Проверяет вывод сообщения об ошибке, возвращённой сервисом."""
        with patch.object(
            self.service,
            "delete_teacher",
            side_effect=ValueError("Преподаватель используется в занятиях."),
        ):
            self._make_cli(["1"]).delete_teacher()

        self.assertEqual(
            self.output_logs,
            ["Ошибка: Преподаватель используется в занятиях."],
        )


if __name__ == "__main__":
    unittest.main()
