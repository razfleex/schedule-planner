import unittest
from pathlib import Path
from runpy import run_path

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from schedule_planner.application import build_role_cli


class DatabaseApplicationTests(unittest.TestCase):
    """Проверяет работу CLI с настоящей базой данных."""

    def setUp(self) -> None:
        """Создаёт изолированную SQLite-базу через Alembic."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
        )

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        migration_path = (
            Path(__file__).resolve().parents[1]
            / "alembic"
            / "versions"
            / "a1b1cc4511b0_create_initial_schedule_tables.py"
        )

        upgrade = run_path(str(migration_path))["upgrade"]

        with self.engine.begin() as connection:
            migration_context = MigrationContext.configure(connection)

            with Operations.context(migration_context):
                upgrade()

        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def tearDown(self) -> None:
        """Закрывает тестовую базу."""
        self.engine.dispose()

    def _run_application(self, answers: list[str]) -> str:
        """Запускает меню с заданными ответами пользователя."""
        user_input = iter(answers)
        output: list[str] = []

        application = build_role_cli(
            input_func=lambda _: next(user_input),
            output=output.append,
            session_factory=self.session_factory,
        )

        application.run()

        return "\n".join(output)

    def _create_schedule(self) -> None:
        """Создаёт справочники и занятие через меню."""
        result = self._run_application(
            [
                "1",
                "9",
                "1",
                "2",
                "1",
                "Иван Иванов",
                "0",
                "2",
                "2",
                "10",
                "ИВТ-261",
                "0",
                "3",
                "2",
                "20",
                "Математика",
                "0",
                "4",
                "2",
                "30",
                "101",
                "0",
                "0",
                "6",
                "100",
                "1",
                "10",
                "20",
                "30",
                "1",
                "09:00",
                "10:30",
                "0",
                "0",
            ]
        )

        self.assertIn("Преподаватель 1 добавлен.", result)
        self.assertIn("Занятие 100 создано.", result)

    def test_schedule_survives_application_restart(self) -> None:
        """Проверяет сохранность расписания после нового запуска."""
        self._create_schedule()

        result = self._run_application(
            [
                "1",
                "1",
                "0",
                "0",
            ]
        )

        self.assertIn(
            "[100] Понедельник 09:00–10:30",
            result,
        )
        self.assertIn("ИВТ-261", result)
        self.assertIn("Математика", result)
        self.assertIn("Иван Иванов", result)

    def test_used_teacher_cannot_be_deleted_via_cli(self) -> None:
        """Проверяет защиту связанных записей в режиме SQLite."""
        self._create_schedule()

        result = self._run_application(
            [
                "1",
                "9",
                "1",
                "4",
                "1",
                "0",
                "0",
                "0",
                "0",
            ]
        )

        self.assertIn(
            "Ошибка: Нельзя удалить преподавателя:",
            result,
        )

        result = self._run_application(
            [
                "1",
                "9",
                "1",
                "1",
                "0",
                "0",
                "0",
                "0",
            ]
        )

        self.assertIn("[1] Иван Иванов", result)


if __name__ == "__main__":
    unittest.main()
