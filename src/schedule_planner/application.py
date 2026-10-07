from collections.abc import Callable

from schedule_planner.catalog_service import CatalogService
from schedule_planner.catalog_usage_checker import CatalogUsageChecker
from schedule_planner.conflicts import LessonConflictChain
from schedule_planner.lesson_management_cli import LessonManagementCli
from schedule_planner.lesson_repository import InMemoryLessonRepository
from schedule_planner.role_cli import RoleCli
from schedule_planner.schedule_cli import ScheduleCli
from schedule_planner.schedule_service import ScheduleService


def build_role_cli(
    input_func: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
) -> RoleCli:
    """Создаёт связанные компоненты терминального приложения."""
    lesson_repository = InMemoryLessonRepository()

    catalog_service = CatalogService(
        usage_checker=CatalogUsageChecker(lesson_repository),
    )

    schedule_service = ScheduleService(
        lesson_repository,
        LessonConflictChain(),
    )

    schedule_cli = ScheduleCli(
        schedule_service,
        output,
    )

    lesson_management_cli = LessonManagementCli(
        schedule_service=schedule_service,
        catalog_service=catalog_service,
        input_func=input_func,
        output=output,
    )

    return RoleCli(
        schedule_cli=schedule_cli,
        lesson_management_cli=lesson_management_cli,
        input_func=input_func,
        output=output,
    )