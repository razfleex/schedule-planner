from schedule_planner.application import build_role_cli
from schedule_planner.database.connection import SessionLocal


def main() -> None:
    """Запускает приложение с постоянным хранением данных в SQLite."""
    build_role_cli(session_factory=SessionLocal).run()
