from collections.abc import Callable

from sqlalchemy.orm import Session

from schedule_planner.catalog_cli import CatalogCli
from schedule_planner.catalog_service import CatalogService
from schedule_planner.catalog_usage_checker import CatalogUsageChecker
from schedule_planner.conflicts import LessonConflictChain
from schedule_planner.database.catalog_repository import (
    SqlAlchemyClassroomRepository,
    SqlAlchemyGroupRepository,
    SqlAlchemySubjectRepository,
    SqlAlchemyTeacherRepository,
)
from schedule_planner.database.lesson_repository import (
    SqlAlchemyLessonRepository,
)
from schedule_planner.lesson_management_cli import LessonManagementCli
from schedule_planner.lesson_repository import InMemoryLessonRepository
from schedule_planner.role_cli import RoleCli
from schedule_planner.schedule_cli import ScheduleCli
from schedule_planner.schedule_service import ScheduleService


def build_role_cli(
    input_func: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
    *,
    session_factory: Callable[[], Session] | None = None,
) -> RoleCli:
    """Создаёт терминальное приложение с выбранным способом хранения."""
    if session_factory is None:
        lesson_repository = InMemoryLessonRepository()

        catalog_service = CatalogService(
            usage_checker=CatalogUsageChecker(lesson_repository),
        )
    else:
        lesson_repository = SqlAlchemyLessonRepository(session_factory)

        catalog_service = CatalogService(
            teacher_repo=SqlAlchemyTeacherRepository(session_factory),
            group_repo=SqlAlchemyGroupRepository(session_factory),
            subject_repo=SqlAlchemySubjectRepository(session_factory),
            classroom_repo=SqlAlchemyClassroomRepository(session_factory),
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

    catalog_cli = CatalogCli(
        catalog_service=catalog_service,
        input_func=input_func,
        output=output,
    )

    return RoleCli(
        schedule_cli=schedule_cli,
        lesson_management_cli=lesson_management_cli,
        catalog_cli=catalog_cli,
        input_func=input_func,
        output=output,
    )
