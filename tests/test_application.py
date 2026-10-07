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


if __name__ == "__main__":
    unittest.main()