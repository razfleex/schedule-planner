from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parents[3] / "instance" / "schedule_planner.db"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


@event.listens_for(engine, "connect")
def _enable_foreign_keys(
    dbapi_connection: Connection,
    _connection_record: object,
) -> None:
    """Включает проверку внешних ключей SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_session() -> Session:
    """Создаёт сессию для работы с базой данных."""
    return SessionLocal()
