import unittest
from collections.abc import Iterator
from pathlib import Path
from runpy import run_path

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from schedule_planner.api import app
from schedule_planner.database.unit_of_work import SqlAlchemyUnitOfWork
from schedule_planner.dependencies import get_unit_of_work


class ApiTestBase(unittest.TestCase):
    """Общая основа интеграционных тестов API."""

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
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

        def override_unit_of_work() -> Iterator[SqlAlchemyUnitOfWork]:
            with SqlAlchemyUnitOfWork(self.session_factory) as unit_of_work:
                yield unit_of_work

        app.dependency_overrides[get_unit_of_work] = override_unit_of_work

        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        app.dependency_overrides.pop(get_unit_of_work, None)
        self.engine.dispose()
