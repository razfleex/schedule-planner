from schedule_planner.application import build_role_cli


def main() -> None:
    """Запускает терминальную программу планирования расписания."""
    build_role_cli().run()