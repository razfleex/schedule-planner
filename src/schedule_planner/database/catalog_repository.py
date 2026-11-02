from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from schedule_planner.database.base import Base
from schedule_planner.database.catalog_mappers import (
    ClassroomMapper,
    GroupMapper,
    SubjectMapper,
    TeacherMapper,
)
from schedule_planner.database.catalog_models import (
    ClassroomORM,
    GroupORM,
    SubjectORM,
    TeacherORM,
)
from schedule_planner.database.session_manager import RepositorySessionManager
from schedule_planner.models import Classroom, Group, Subject, Teacher


class HasId(Protocol):
    """Протокол для сущностей с целочисленным идентификатором."""

    id: int


class EntityMapper[TEntity, TORModel](Protocol):
    """Протокол преобразования доменных и ORM-моделей."""

    @staticmethod
    def to_orm(entity: TEntity) -> TORModel: ...

    @staticmethod
    def to_domain(orm_entity: TORModel) -> TEntity: ...


class BaseSqlAlchemyCatalogRepository[TEntity: HasId, TORModel: Base]:
    """Базовый SQLAlchemy-репозиторий с поддержкой Unit of Work."""

    def __init__(
        self,
        session_factory: Callable[[], Session] | Session,
        model_cls: type[TORModel],
        mapper: type[EntityMapper[TEntity, TORModel]],
    ) -> None:
        """Принимает фабрику сессий или готовую сессию."""
        self._sessions = RepositorySessionManager(session_factory)
        self._model_cls = model_cls
        self._mapper = mapper

    def add(self, entity: TEntity) -> TEntity:
        """Добавляет сущность в базу данных."""
        with self._sessions.open() as session:
            try:
                if session.get(self._model_cls, entity.id) is not None:
                    raise ValueError(f"Сущность с id={entity.id} уже существует.")

                orm_entity = self._mapper.to_orm(entity)
                session.add(orm_entity)

                self._sessions.save(session)
                return self._mapper.to_domain(orm_entity)

            except IntegrityError as exc:
                raise ValueError(
                    f"Сущность с id={entity.id} уже существует "
                    "или нарушены ограничения БД."
                ) from exc

    def get_by_id(self, entity_id: int) -> TEntity | None:
        """Возвращает сущность по id или None."""
        with self._sessions.open() as session:
            orm_entity = session.get(self._model_cls, entity_id)

            if orm_entity is None:
                return None

            return self._mapper.to_domain(orm_entity)

    def get_all(self) -> list[TEntity]:
        """Возвращает все сущности по возрастанию id."""
        with self._sessions.open() as session:
            stmt = select(self._model_cls).order_by(self._model_cls.id.asc())
            orm_entities = session.scalars(stmt).all()

            return [self._mapper.to_domain(item) for item in orm_entities]

    def update(self, entity: TEntity) -> TEntity:
        """Обновляет существующую сущность."""
        with self._sessions.open() as session:
            orm_entity = session.get(self._model_cls, entity.id)

            if orm_entity is None:
                raise ValueError(
                    f"Сущность с id={entity.id} не найдена для обновления."
                )

            new_orm = self._mapper.to_orm(entity)

            for column in self._model_cls.__table__.columns:
                if not column.primary_key:
                    setattr(
                        orm_entity,
                        column.name,
                        getattr(new_orm, column.name),
                    )

            try:
                self._sessions.save(session)
            except IntegrityError as exc:
                raise ValueError(
                    "Ошибка целостности данных при обновлении "
                    f"сущности с id={entity.id}."
                ) from exc

            return self._mapper.to_domain(orm_entity)

    def delete(self, entity_id: int) -> None:
        """Удаляет сущность из базы данных."""
        with self._sessions.open() as session:
            orm_entity = session.get(self._model_cls, entity_id)

            if orm_entity is None:
                raise ValueError(f"Сущность с id={entity_id} не найдена для удаления.")

            session.delete(orm_entity)

            try:
                self._sessions.save(session)
            except IntegrityError as exc:
                raise ValueError(
                    f"Невозможно удалить сущность с id={entity_id}, "
                    "так как она используется в расписании."
                ) from exc


class SqlAlchemyTeacherRepository(BaseSqlAlchemyCatalogRepository[Teacher, TeacherORM]):
    """SQLAlchemy-репозиторий преподавателей."""

    def __init__(
        self,
        session_factory: Callable[[], Session] | Session,
    ) -> None:
        """Инициализирует репозиторий преподавателей."""
        super().__init__(
            session_factory,
            TeacherORM,
            TeacherMapper,
        )


class SqlAlchemyGroupRepository(BaseSqlAlchemyCatalogRepository[Group, GroupORM]):
    """SQLAlchemy-репозиторий учебных групп."""

    def __init__(
        self,
        session_factory: Callable[[], Session] | Session,
    ) -> None:
        """Инициализирует репозиторий учебных групп."""
        super().__init__(
            session_factory,
            GroupORM,
            GroupMapper,
        )


class SqlAlchemySubjectRepository(BaseSqlAlchemyCatalogRepository[Subject, SubjectORM]):
    """SQLAlchemy-репозиторий учебных дисциплин."""

    def __init__(
        self,
        session_factory: Callable[[], Session] | Session,
    ) -> None:
        """Инициализирует репозиторий дисциплин."""
        super().__init__(
            session_factory,
            SubjectORM,
            SubjectMapper,
        )


class SqlAlchemyClassroomRepository(
    BaseSqlAlchemyCatalogRepository[Classroom, ClassroomORM]
):
    """SQLAlchemy-репозиторий аудиторий."""

    def __init__(
        self,
        session_factory: Callable[[], Session] | Session,
    ) -> None:
        """Инициализирует репозиторий аудиторий."""
        super().__init__(
            session_factory,
            ClassroomORM,
            ClassroomMapper,
        )
