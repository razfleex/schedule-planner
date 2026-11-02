from collections.abc import Callable, Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session


class RepositorySessionManager:
    """Поддерживает автономные и внешние SQLAlchemy-сессии."""

    def __init__(
        self,
        session_source: Callable[[], Session] | Session,
    ) -> None:
        self._session_source = session_source

    @contextmanager
    def open(self) -> Iterator[Session]:
        """Предоставляет сессию, не закрывая внешнюю."""
        if isinstance(self._session_source, Session):
            yield self._session_source
        else:
            with self._session_source() as session:
                yield session

    def save(self, session: Session) -> None:
        """Сохраняет изменения согласно режиму работы."""
        if isinstance(self._session_source, Session):
            session.flush()
        else:
            session.commit()
