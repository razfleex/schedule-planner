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
from schedule_planner.models import Classroom, Group, Subject, Teacher


class HasId(Protocol):
    """Протокол для сущностей с целочисленным идентификатором."""

    id: int


class EntityMapper[TEntity, TORModel](Protocol):
    """Протокол для мапперов между доменными сущностями и ORM-моделями."""

    @staticmethod
    def to_orm(entity: TEntity) -> TORModel: ...

    @staticmethod
    def to_domain(orm_entity: TORModel) -> TEntity: ...


class BaseSqlAlchemyCatalogRepository[TEntity: HasId, TORModel: Base]:
    """Базовый SQLAlchemy-репозиторий для справочных сущностей."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
        model_cls: type[TORModel],
        mapper: type[EntityMapper[TEntity, TORModel]],
    ) -> None:
        """Инициализирует репозиторий фабрикой сессий, классом ORM-модели и маппером."""
        self._session_factory = session_factory
        self._model_cls = model_cls
        self._mapper = mapper

    def add(self, entity: TEntity) -> TEntity:
        """Добавляет сущность в базу данных.

        Raises:
            ValueError: Если запись с таким id уже существует или нарушены ограничения БД.
        """
        with self._session_factory() as session:
            try:
                if session.get(self._model_cls, entity.id) is not None:
                    raise ValueError(f"Сущность с id={entity.id} уже существует.")
                orm_entity = self._mapper.to_orm(entity)
                session.add(orm_entity)
                session.commit()
                return self._mapper.to_domain(orm_entity)
            except ValueError:
                session.rollback()
                raise
            except IntegrityError as exc:
                session.rollback()
                raise ValueError(
                    f"Сущность с id={entity.id} уже существует или нарушены ограничения БД."
                ) from exc
            except Exception:
                session.rollback()
                raise

    def get_by_id(self, entity_id: int) -> TEntity | None:
        """Возвращает сущность по id или None, если запись не найдена."""
        with self._session_factory() as session:
            orm_entity = session.get(self._model_cls, entity_id)
            if orm_entity is None:
                return None
            return self._mapper.to_domain(orm_entity)

    def get_all(self) -> list[TEntity]:
        """Возвращает список всех сущностей в порядке возрастания id."""
        with self._session_factory() as session:
            stmt = select(self._model_cls).order_by(self._model_cls.id.asc())
            orm_entities = session.scalars(stmt).all()
            return [self._mapper.to_domain(item) for item in orm_entities]

    def update(self, entity: TEntity) -> TEntity:
        """Обновляет существующую запись в базе данных.

        Raises:
            ValueError: Если сущность не найдена или нарушена целостность данных.
        """
        with self._session_factory() as session:
            try:
                orm_entity = session.get(self._model_cls, entity.id)
                if orm_entity is None:
                    raise ValueError(
                        f"Сущность с id={entity.id} не найдена для обновления."
                    )
                new_orm = self._mapper.to_orm(entity)
                for column in self._model_cls.__table__.columns:
                    if not column.primary_key:
                        setattr(orm_entity, column.name, getattr(new_orm, column.name))
                session.commit()
                return self._mapper.to_domain(orm_entity)
            except ValueError:
                session.rollback()
                raise
            except IntegrityError as exc:
                session.rollback()
                raise ValueError(
                    f"Ошибка целостности данных при обновлении сущности с id={entity.id}."
                ) from exc
            except Exception:
                session.rollback()
                raise

    def delete(self, entity_id: int) -> None:
        """Удаляет запись по id.

        Raises:
            ValueError: Если сущность не найдена или используется в других записях.
        """
        with self._session_factory() as session:
            try:
                orm_entity = session.get(self._model_cls, entity_id)
                if orm_entity is None:
                    raise ValueError(
                        f"Сущность с id={entity_id} не найдена для удаления."
                    )
                session.delete(orm_entity)
                session.commit()
            except ValueError:
                session.rollback()
                raise
            except IntegrityError as exc:
                session.rollback()
                raise ValueError(
                    f"Невозможно удалить сущность с id={entity_id}, так как она используется в расписании."
                ) from exc
            except Exception:
                session.rollback()
                raise


class SqlAlchemyTeacherRepository(BaseSqlAlchemyCatalogRepository[Teacher, TeacherORM]):
    """SQLAlchemy-репозиторий для преподавателей."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        """Инициализирует репозиторий преподавателей."""
        super().__init__(session_factory, TeacherORM, TeacherMapper)


class SqlAlchemyGroupRepository(BaseSqlAlchemyCatalogRepository[Group, GroupORM]):
    """SQLAlchemy-репозиторий для учебных групп."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        """Инициализирует репозиторий учебных групп."""
        super().__init__(session_factory, GroupORM, GroupMapper)


class SqlAlchemySubjectRepository(BaseSqlAlchemyCatalogRepository[Subject, SubjectORM]):
    """SQLAlchemy-репозиторий для учебных дисциплин."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        """Инициализирует репозиторий дисциплин."""
        super().__init__(session_factory, SubjectORM, SubjectMapper)


class SqlAlchemyClassroomRepository(
    BaseSqlAlchemyCatalogRepository[Classroom, ClassroomORM]
):
    """SQLAlchemy-репозиторий для аудиторий."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        """Инициализирует репозиторий аудиторий."""
        super().__init__(session_factory, ClassroomORM, ClassroomMapper)
