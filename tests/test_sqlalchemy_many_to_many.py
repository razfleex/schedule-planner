import unittest
from datetime import time
from pathlib import Path
from runpy import run_path

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from schedule_planner.database.catalog_models import (
    ClassroomORM,
    GroupORM,
    SubjectORM,
    TeacherORM,
)
from schedule_planner.database.lesson_model import LessonORM
from schedule_planner.models import Weekday


class ManyToManyRelationshipTests(unittest.TestCase):
    """Проверяет связь групп и дисциплин через занятия."""

    def setUp(self) -> None:
        """Подготавливает тестовую SQLite-базу через Alembic."""
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
            context = MigrationContext.configure(connection)

            with Operations.context(context):
                upgrade()

        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

        with self.session_factory() as session:
            session.add_all(
                [
                    TeacherORM(id=1, full_name="Иванов И. И."),
                    GroupORM(id=10, name="ИВТ-261"),
                    GroupORM(id=11, name="ИВТ-262"),
                    SubjectORM(id=20, name="Математика"),
                    SubjectORM(id=21, name="Физика"),
                    ClassroomORM(id=30, name="А-101"),
                ]
            )

            session.flush()

            lesson_data = [
                (100, 10, 20, Weekday.MONDAY),
                (101, 10, 21, Weekday.TUESDAY),
                (102, 11, 20, Weekday.WEDNESDAY),
                (103, 10, 20, Weekday.THURSDAY),
            ]

            for lesson_id, group_id, subject_id, day in lesson_data:
                session.add(
                    LessonORM(
                        id=lesson_id,
                        teacher_id=1,
                        group_id=group_id,
                        subject_id=subject_id,
                        classroom_id=30,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(10, 30),
                    )
                )

            session.commit()

    def tearDown(self) -> None:
        """Освобождает тестовую базу данных."""
        self.engine.dispose()

    def test_group_has_multiple_subjects(self) -> None:
        """Одна группа может изучать несколько дисциплин."""
        with self.session_factory() as session:
            group = session.get(GroupORM, 10)

            self.assertIsNotNone(group)

            subjects = {subject.name for subject in group.subjects}

            self.assertEqual(
                subjects,
                {"Математика", "Физика"},
            )

            self.assertEqual(len(group.subjects), 2)

    def test_subject_has_multiple_groups(self) -> None:
        """Одну дисциплину могут изучать несколько групп."""
        with self.session_factory() as session:
            subject = session.get(SubjectORM, 20)

            self.assertIsNotNone(subject)

            groups = {group.name for group in subject.groups}

            self.assertEqual(
                groups,
                {"ИВТ-261", "ИВТ-262"},
            )

            self.assertEqual(len(subject.groups), 2)

    def test_relationship_is_read_only(self) -> None:
        """Изменение коллекции не создаёт занятие в БД."""
        with self.session_factory() as session:
            group = session.get(GroupORM, 11)
            subject = session.get(SubjectORM, 21)

            self.assertIsNotNone(group)
            self.assertIsNotNone(subject)

            group.subjects.append(subject)
            session.commit()

        with self.session_factory() as session:
            group = session.get(GroupORM, 11)

            subject_ids = [subject.id for subject in group.subjects]

            self.assertEqual(subject_ids, [20])


if __name__ == "__main__":
    unittest.main()
