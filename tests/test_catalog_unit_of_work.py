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


class CatalogUnitOfWorkTests(unittest.TestCase):
    """Проверяет общие транзакции репозиториев."""

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
            """Включает внешние ключи SQLite."""
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

        self.teacher = Teacher(1, "Иванов И. И.")
        self.group = Group(10, "ИВТ-261")
        self.subject = Subject(20, "Математика")
        self.classroom = Classroom(30, "101")

    def tearDown(self) -> None:
        """Закрывает тестовую базу."""
        self.engine.dispose()

    def test_commit_saves_multiple_catalogs(self) -> None:
        """Проверяет сохранение нескольких справочников."""
        with SqlAlchemyUnitOfWork(self.session_factory) as uow:
            teacher_repo = SqlAlchemyTeacherRepository(uow.session)
            group_repo = SqlAlchemyGroupRepository(uow.session)
            subject_repo = SqlAlchemySubjectRepository(uow.session)
            classroom_repo = SqlAlchemyClassroomRepository(uow.session)

            teacher_repo.add(self.teacher)
            group_repo.add(self.group)
            subject_repo.add(self.subject)
            classroom_repo.add(self.classroom)

            uow.commit()

        self.assertEqual(
            SqlAlchemyTeacherRepository(self.session_factory).get_by_id(1),
            self.teacher,
        )
        self.assertEqual(
            SqlAlchemyGroupRepository(self.session_factory).get_by_id(10),
            self.group,
        )
        self.assertEqual(
            SqlAlchemySubjectRepository(self.session_factory).get_by_id(20),
            self.subject,
        )
        self.assertEqual(
            SqlAlchemyClassroomRepository(self.session_factory).get_by_id(30),
            self.classroom,
        )

    def test_without_commit_rolls_back_all(self) -> None:
        """Проверяет общий откат без commit."""
        with SqlAlchemyUnitOfWork(self.session_factory) as uow:
            SqlAlchemyTeacherRepository(uow.session).add(self.teacher)
            SqlAlchemyGroupRepository(uow.session).add(self.group)

        self.assertIsNone(
            SqlAlchemyTeacherRepository(self.session_factory).get_by_id(1)
        )
        self.assertIsNone(SqlAlchemyGroupRepository(self.session_factory).get_by_id(10))

    def test_repository_error_rolls_back_all(self) -> None:
        """Проверяет общий откат при ошибке репозитория."""
        with (
            self.assertRaisesRegex(ValueError, "уже существует"),
            SqlAlchemyUnitOfWork(self.session_factory) as uow,
        ):
            teacher_repo = SqlAlchemyTeacherRepository(uow.session)
            group_repo = SqlAlchemyGroupRepository(uow.session)

            teacher_repo.add(self.teacher)
            group_repo.add(self.group)
            teacher_repo.add(self.teacher)

        self.assertIsNone(
            SqlAlchemyTeacherRepository(self.session_factory).get_by_id(1)
        )
        self.assertIsNone(SqlAlchemyGroupRepository(self.session_factory).get_by_id(10))

    def test_catalogs_and_lesson_share_transaction(self) -> None:
        """Проверяет общую транзакцию справочников и занятия."""
        lesson = Lesson(
            id=100,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

        with SqlAlchemyUnitOfWork(self.session_factory) as uow:
            SqlAlchemyTeacherRepository(uow.session).add(self.teacher)
            SqlAlchemyGroupRepository(uow.session).add(self.group)
            SqlAlchemySubjectRepository(uow.session).add(self.subject)
            SqlAlchemyClassroomRepository(uow.session).add(self.classroom)

            lesson_repo = SqlAlchemyLessonRepository(uow.session)
            lesson_repo.add(lesson)

            self.assertEqual(
                lesson_repo.get_by_id(100),
                lesson,
            )

            uow.commit()

        saved = SqlAlchemyLessonRepository(self.session_factory).get_by_id(100)

        self.assertEqual(saved, lesson)


if __name__ == "__main__":
    unittest.main()
