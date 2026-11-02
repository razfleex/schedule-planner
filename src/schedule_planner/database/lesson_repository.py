from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from schedule_planner.database.lesson_mapper import LessonMapper
from schedule_planner.database.lesson_model import LessonORM
from schedule_planner.models import Lesson


class SqlAlchemyLessonRepository:
    """Репозиторий занятий с хранением в базе данных."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
    ) -> None:
        """Принимает фабрику сессий SQLAlchemy."""
        self._session_factory = session_factory

    @staticmethod
    def _query():
        """Создаёт запрос с загрузкой связанных справочников."""
        return select(LessonORM).options(
            joinedload(LessonORM.teacher),
            joinedload(LessonORM.group),
            joinedload(LessonORM.subject),
            joinedload(LessonORM.classroom),
        )

    def add(self, lesson: Lesson) -> None:
        """Добавляет новое занятие."""
        with self._session_factory() as session:
            session.add(LessonMapper.to_orm(lesson))

            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise ValueError(
                    f"Не удалось добавить занятие {lesson.id}: "
                    "нарушено ограничение базы данных."
                ) from error

    def get_by_id(self, lesson_id: int) -> Lesson | None:
        """Возвращает занятие по ID или None."""
        with self._session_factory() as session:
            query = self._query().where(
                LessonORM.id == lesson_id,
            )
            orm_lesson = session.scalars(query).one_or_none()

            if orm_lesson is None:
                return None

            return LessonMapper.to_domain(orm_lesson)

    def get_all(self) -> list[Lesson]:
        """Возвращает все занятия по возрастанию ID."""
        with self._session_factory() as session:
            query = self._query().order_by(LessonORM.id)
            orm_lessons = session.scalars(query).all()

            return [LessonMapper.to_domain(orm_lesson) for orm_lesson in orm_lessons]

    def update(self, lesson: Lesson) -> None:
        """Обновляет существующее занятие."""
        with self._session_factory() as session:
            stored = session.get(LessonORM, lesson.id)

            if stored is None:
                raise ValueError(f"Занятие с идентификатором {lesson.id} не найдено.")

            stored.teacher_id = lesson.teacher.id
            stored.group_id = lesson.group.id
            stored.subject_id = lesson.subject.id
            stored.classroom_id = lesson.classroom.id
            stored.day_of_week = lesson.day_of_week
            stored.start_time = lesson.start_time
            stored.end_time = lesson.end_time

            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise ValueError(
                    f"Не удалось обновить занятие {lesson.id}: "
                    "нарушено ограничение базы данных."
                ) from error

    def delete(self, lesson_id: int) -> None:
        """Удаляет занятие по ID."""
        with self._session_factory() as session:
            stored = session.get(LessonORM, lesson_id)

            if stored is None:
                raise ValueError(f"Занятие с идентификатором {lesson_id} не найдено.")

            session.delete(stored)
            session.commit()
