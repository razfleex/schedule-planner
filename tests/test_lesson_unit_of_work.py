import unittest
from datetime import time
from pathlib import Path
from runpy import run_path
from sqlite3 import Connection

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from schedule_planner.database.catalog_repository import (
    SqlAlchemyClassroomRepository,
    SqlAlchemyGroupRepository,
    SqlAlchemySubjectRepository,
    SqlAlchemyTeacherRepository,
)
from schedule_planner.database.lesson_repository import (
    SqlAlchemyLessonRepository,
)
from schedule_planner.database.unit_of_work import SqlAlchemyUnitOfWork
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class LessonUnitOfWorkTests(unittest.TestCase):
    """Проверяет работу репозитория занятий через Unit of Work."""

    def setUp(self) -> None:
        """Создаёт изолированную SQLite-базу через Alembic."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
        )

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(
            dbapi_connection: Connection,
            _connection_record: object,
        ) -> None:
            """Включает проверку внешних ключей."""
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
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                upgrade()

        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

        teacher = Teacher(1, "Иванов И. И.")
        group = Group(10, "ИВТ-261")
        subject = Subject(20, "Математика")
        classroom = Classroom(30, "101")

        SqlAlchemyTeacherRepository(self.session_factory).add(teacher)
        SqlAlchemyGroupRepository(self.session_factory).add(group)
        SqlAlchemySubjectRepository(self.session_factory).add(subject)
        SqlAlchemyClassroomRepository(self.session_factory).add(classroom)

        self.lesson = Lesson(
            id=100,
            teacher=teacher,
            group=group,
            subject=subject,
            classroom=classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

    def tearDown(self) -> None:
        """Закрывает тестовую базу."""
        self.engine.dispose()

    def test_commit_persists_lesson(self) -> None:
        """Проверяет сохранение после подтверждения транзакции."""
        with SqlAlchemyUnitOfWork(self.session_factory) as uow:
            repository = SqlAlchemyLessonRepository(uow.session)
            repository.add(self.lesson)

            self.assertEqual(
                repository.get_by_id(100),
                self.lesson,
            )

            uow.commit()

        repository = SqlAlchemyLessonRepository(self.session_factory)
        self.assertEqual(repository.get_by_id(100), self.lesson)

    def test_without_commit_rolls_back(self) -> None:
        """Проверяет отмену изменений без подтверждения."""
        with SqlAlchemyUnitOfWork(self.session_factory) as uow:
            repository = SqlAlchemyLessonRepository(uow.session)
            repository.add(self.lesson)

        repository = SqlAlchemyLessonRepository(self.session_factory)
        self.assertIsNone(repository.get_by_id(100))

    def test_exception_rolls_back(self) -> None:
        """Проверяет отмену изменений при исключении."""
        with (
            self.assertRaisesRegex(ValueError, "Ошибка операции"),
            SqlAlchemyUnitOfWork(self.session_factory) as uow,
        ):
            repository = SqlAlchemyLessonRepository(uow.session)
            repository.add(self.lesson)
            raise ValueError("Ошибка операции")

        repository = SqlAlchemyLessonRepository(self.session_factory)
        self.assertIsNone(repository.get_by_id(100))


if __name__ == "__main__":
    unittest.main()
