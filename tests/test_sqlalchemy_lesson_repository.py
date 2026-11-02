import unittest
from datetime import time
from pathlib import Path
from runpy import run_path

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
from schedule_planner.database.lesson_mapper import LessonMapper
from schedule_planner.database.lesson_repository import (
    SqlAlchemyLessonRepository,
)
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
    Weekday,
)


class SqlAlchemyLessonRepositoryTests(unittest.TestCase):
    """Проверяет репозиторий на изолированной SQLite-базе."""

    def setUp(self) -> None:
        """Создаёт временную БД через миграцию Alembic."""
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

        self.teacher = Teacher(1, "Иванов И. И.")
        self.group = Group(10, "ИВТ-261")
        self.subject = Subject(20, "Программная инженерия")
        self.classroom = Classroom(30, "А-101")

        self.teacher_repo = SqlAlchemyTeacherRepository(self.session_factory)
        self.group_repo = SqlAlchemyGroupRepository(self.session_factory)
        self.subject_repo = SqlAlchemySubjectRepository(self.session_factory)
        self.classroom_repo = SqlAlchemyClassroomRepository(self.session_factory)

        self.teacher_repo.add(self.teacher)
        self.group_repo.add(self.group)
        self.subject_repo.add(self.subject)
        self.classroom_repo.add(self.classroom)

        self.repository = SqlAlchemyLessonRepository(self.session_factory)

        self.lesson = Lesson(
            id=100,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 30),
        )

    def tearDown(self) -> None:
        """Освобождает временную базу данных."""
        self.engine.dispose()

    def test_lesson_mapper_to_orm(self) -> None:
        """Проверяет преобразование занятия во внешние ключи."""
        orm_lesson = LessonMapper.to_orm(self.lesson)

        self.assertEqual(orm_lesson.id, 100)
        self.assertEqual(orm_lesson.teacher_id, 1)
        self.assertEqual(orm_lesson.group_id, 10)
        self.assertEqual(orm_lesson.subject_id, 20)
        self.assertEqual(orm_lesson.classroom_id, 30)
        self.assertEqual(orm_lesson.day_of_week, Weekday.MONDAY)

    def test_save_and_read_lesson(self) -> None:
        """Проверяет сохранение и загрузку занятия."""
        self.repository.add(self.lesson)

        saved = self.repository.get_by_id(100)

        self.assertEqual(saved, self.lesson)

    def test_get_all_lessons(self) -> None:
        """Проверяет получение списка занятий."""
        self.repository.add(self.lesson)

        self.assertEqual(
            self.repository.get_all(),
            [self.lesson],
        )

    def test_data_survives_new_repository_instance(self) -> None:
        """Проверяет сохранность данных между сессиями."""
        self.repository.add(self.lesson)

        another_repository = SqlAlchemyLessonRepository(self.session_factory)

        self.assertEqual(
            another_repository.get_by_id(100),
            self.lesson,
        )

    def test_update_lesson(self) -> None:
        """Проверяет изменение сохранённого занятия."""
        self.repository.add(self.lesson)

        updated = Lesson(
            id=100,
            teacher=self.teacher,
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.TUESDAY,
            start_time=time(11, 0),
            end_time=time(12, 30),
        )

        self.repository.update(updated)

        self.assertEqual(
            self.repository.get_by_id(100),
            updated,
        )

    def test_delete_lesson(self) -> None:
        """Проверяет удаление сохранённого занятия."""
        self.repository.add(self.lesson)

        self.repository.delete(100)

        self.assertIsNone(self.repository.get_by_id(100))

    def test_duplicate_lesson_is_rejected(self) -> None:
        """Проверяет запрет повторного идентификатора."""
        self.repository.add(self.lesson)

        with self.assertRaises(ValueError):
            self.repository.add(self.lesson)

    def test_missing_lesson_is_rejected(self) -> None:
        """Проверяет обработку отсутствующих записей."""
        self.assertIsNone(self.repository.get_by_id(999))

        with self.assertRaises(ValueError):
            self.repository.update(self.lesson)

        with self.assertRaises(ValueError):
            self.repository.delete(999)

    def test_unknown_teacher_is_rejected(self) -> None:
        """Проверяет ограничение внешнего ключа."""
        invalid_lesson = Lesson(
            id=101,
            teacher=Teacher(999, "Неизвестный"),
            group=self.group,
            subject=self.subject,
            classroom=self.classroom,
            day_of_week=Weekday.MONDAY,
            start_time=time(11, 0),
            end_time=time(12, 30),
        )

        with self.assertRaises(ValueError):
            self.repository.add(invalid_lesson)

        self.assertIsNone(self.repository.get_by_id(101))

    def test_used_teacher_cannot_be_deleted(self) -> None:
        """Проверяет запрет удаления связанного преподавателя."""
        self.repository.add(self.lesson)

        with self.assertRaises(ValueError):
            self.teacher_repo.delete(1)

        self.assertEqual(
            self.teacher_repo.get_by_id(1),
            self.teacher,
        )


if __name__ == "__main__":
    unittest.main()
