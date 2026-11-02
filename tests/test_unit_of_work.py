import unittest
from unittest.mock import create_autospec

from sqlalchemy.orm import Session

from schedule_planner.database.unit_of_work import SqlAlchemyUnitOfWork


class SqlAlchemyUnitOfWorkTests(unittest.TestCase):
    """Проверяет управление сессией и транзакциями."""

    def setUp(self) -> None:
        self.session = create_autospec(Session, instance=True)
        self.uow = SqlAlchemyUnitOfWork(lambda: self.session)

    def test_commit(self) -> None:
        """Проверяет подтверждение изменений."""
        with self.uow as uow:
            self.assertIs(uow.session, self.session)
            uow.commit()

        self.session.commit.assert_called_once()
        self.session.close.assert_called_once()

    def test_rollback_without_commit(self) -> None:
        """Проверяет отмену неподтверждённых изменений."""
        with self.uow:
            pass

        self.session.rollback.assert_called_once()
        self.session.commit.assert_not_called()
        self.session.close.assert_called_once()

    def test_rollback_on_exception(self) -> None:
        """Проверяет откат и закрытие при ошибке."""
        with self.assertRaisesRegex(ValueError, "Ошибка операции"), self.uow:
            raise ValueError("Ошибка операции")

        self.session.rollback.assert_called_once()
        self.session.commit.assert_not_called()
        self.session.close.assert_called_once()

    def test_session_unavailable_outside_context(self) -> None:
        """Проверяет запрет обращения к неактивной сессии."""
        with self.assertRaises(RuntimeError):
            _ = self.uow.session

    def test_repeated_entry_is_rejected(self) -> None:
        """Проверяет запрет повторного открытия активного UoW."""
        with self.uow, self.assertRaises(RuntimeError):
            self.uow.__enter__()

        self.session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
