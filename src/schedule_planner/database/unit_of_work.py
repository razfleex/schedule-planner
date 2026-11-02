from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:
    """Управляет общей SQLAlchemy-сессией и транзакцией."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        """Возвращает активную сессию."""
        if self._session is None:
            raise RuntimeError("Unit of Work не активен.")
        return self._session

    def __enter__(self) -> Self:
        """Открывает сессию для выполнения операции."""
        if self._session is not None:
            raise RuntimeError("Unit of Work уже активен.")

        self._session = self._session_factory()
        return self

    def commit(self) -> None:
        """Подтверждает изменения."""
        self.session.commit()

    def rollback(self) -> None:
        """Отменяет неподтверждённые изменения."""
        self.session.rollback()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Откатывает неподтверждённые изменения и закрывает сессию."""
        session = self.session

        try:
            session.rollback()
        finally:
            session.close()
            self._session = None
