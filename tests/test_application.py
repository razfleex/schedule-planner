import unittest

from schedule_planner.application import build_role_cli


class ApplicationTests(unittest.TestCase):
    """Проверяет сборку терминального приложения."""

    def test_application_can_start_and_exit(self) -> None:
        """Проверяет запуск главного меню и корректное завершение."""
        answers = iter(["0"])
        output: list[str] = []

        application = build_role_cli(
            input_func=lambda _: next(answers),
            output=output.append,
        )

        application.run()

        text = "\n".join(output)

        self.assertIn("Выберите роль:", text)
        self.assertIn("Работа программы завершена.", text)

    def test_catalog_lessons_and_deletion_guard_work_together(self) -> None:
        """Проверяет создание занятия и защиту используемого преподавателя."""
        answers = iter(
            [
                "1", "9",
                "1", "2", "1", "Иван Иванов", "0",
                "2", "2", "10", "ИВТ-261", "0",
                "3", "2", "20", "Математика", "0",
                "4", "2", "30", "101", "0",
                "0",
                "6", "100", "1", "10", "20", "30",
                "1", "09:00", "10:30",
                "9", "1", "4", "1", "0", "0",
                "1",
                "8", "100",
                "9", "1", "4", "1", "0", "0",
                "0", "0",
            ]
        )

        output: list[str] = []

        application = build_role_cli(
            input_func=lambda _: next(answers),
            output=output.append,
        )

        application.run()

        text = "\n".join(output)

        self.assertIn("Преподаватель 1 добавлен.", text)
        self.assertIn("Занятие 100 создано.", text)
        self.assertIn("[100] Понедельник 09:00–10:30", text)
        self.assertIn("Ошибка: Нельзя удалить преподавателя:", text)
        self.assertIn("Занятие 100 удалено.", text)
        self.assertIn("Преподаватель 1 удалён.", text)


if __name__ == "__main__":
    unittest.main()