import unittest
from unittest.mock import MagicMock

from schedule_planner.role_cli import RoleCli


class RoleCliTests(unittest.TestCase):
    """Проверяет меню и ограничения ролей."""

    def setUp(self) -> None:
        """Создаёт подменённые CLI-компоненты для тестов."""
        self.schedule_cli = MagicMock()
        self.lesson_management_cli = MagicMock()
        self.catalog_cli = MagicMock()
        self.output: list[str] = []

    def make_cli(self, answers: list[str]) -> RoleCli:
        """Создаёт меню с подготовленными ответами пользователя."""
        answer_iterator = iter(answers)

        return RoleCli(
            schedule_cli=self.schedule_cli,
            lesson_management_cli=self.lesson_management_cli,
            catalog_cli=self.catalog_cli,
            input_func=lambda _: next(answer_iterator),
            output=self.output.append,
        )

    def test_student_views_group_schedule(self) -> None:
        """Проверяет просмотр расписания Студентом."""
        cli = self.make_cli(["2", "10", "0"])

        cli.run()

        self.schedule_cli.show_student_schedule.assert_called_once_with(10)
        self.lesson_management_cli.create_lesson.assert_not_called()
        self.lesson_management_cli.update_lesson.assert_not_called()
        self.lesson_management_cli.delete_lesson.assert_not_called()

    def test_teacher_views_own_schedule(self) -> None:
        """Проверяет просмотр расписания Преподавателем."""
        cli = self.make_cli(["3", "7", "0"])

        cli.run()

        self.schedule_cli.show_teacher_schedule.assert_called_once_with(7)

    def test_compiler_can_create_lesson(self) -> None:
        """Проверяет доступ Составителя к созданию занятия."""
        cli = self.make_cli(["1", "6", "0", "0"])

        cli.run()

        self.lesson_management_cli.create_lesson.assert_called_once()

    def test_compiler_can_filter_schedule(self) -> None:
        """Проверяет фильтрацию расписания Составителем."""
        cli = self.make_cli(
            [
                "1",
                "2",
                "5",
                "3",
                "8",
                "4",
                "3",
                "5",
                "2",
                "0",
                "0",
            ]
        )

        cli.run()

        self.schedule_cli.show_lessons_by_group.assert_called_once_with(5)
        self.schedule_cli.show_lessons_by_teacher.assert_called_once_with(8)
        self.schedule_cli.show_lessons_by_classroom.assert_called_once_with(3)

    def test_invalid_role_is_reported(self) -> None:
        """Проверяет сообщение при неизвестной роли."""
        cli = self.make_cli(["9", "0"])

        cli.run()

        self.assertIn(
            "Ошибка: неизвестный пункт меню.",
            self.output,
        )

    def test_compiler_can_manage_teachers(self) -> None:
        """Проверяет все операции Составителя с преподавателями."""
        cli = self.make_cli(
            [
                "1",
                "9",
                "1",
                "1",
                "2",
                "3",
                "4",
                "0",
                "0",
                "0",
                "0",
            ]
        )

        cli.run()

        self.catalog_cli.show_teachers.assert_called_once()
        self.catalog_cli.add_teacher.assert_called_once()
        self.catalog_cli.update_teacher.assert_called_once()
        self.catalog_cli.delete_teacher.assert_called_once()

    def test_compiler_can_open_all_catalogs(self) -> None:
        """Проверяет открытие справочников групп, дисциплин и аудиторий."""
        cli = self.make_cli(
            [
                "1",
                "9",
                "2",
                "1",
                "0",
                "3",
                "1",
                "0",
                "4",
                "1",
                "0",
                "0",
                "0",
                "0",
            ]
        )

        cli.run()

        self.catalog_cli.show_groups.assert_called_once()
        self.catalog_cli.show_subjects.assert_called_once()
        self.catalog_cli.show_classrooms.assert_called_once()

    def test_student_and_teacher_cannot_manage_catalogs(self) -> None:
        """Проверяет отсутствие управления справочниками у других ролей."""
        cli = self.make_cli(["2", "10", "3", "7", "0"])

        cli.run()

        self.assertEqual(self.catalog_cli.mock_calls, [])

    def test_invalid_catalog_action_is_reported(self) -> None:
        """Проверяет сообщение при неправильной команде справочника."""
        cli = self.make_cli(
            ["1", "9", "1", "8", "0", "0", "0", "0"]
        )

        cli.run()

        self.assertIn(
            "Ошибка: неизвестный пункт меню.",
            self.output,
        )


if __name__ == "__main__":
    unittest.main()