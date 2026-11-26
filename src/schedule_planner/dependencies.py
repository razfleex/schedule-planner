from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends

from schedule_planner.catalog_service import CatalogService
from schedule_planner.catalog_usage_checker import CatalogUsageChecker
from schedule_planner.conflicts import LessonConflictChain
from schedule_planner.database.catalog_repository import (
    SqlAlchemyClassroomRepository,
    SqlAlchemyGroupRepository,
    SqlAlchemySubjectRepository,
    SqlAlchemyTeacherRepository,
)
from schedule_planner.database.connection import create_session
from schedule_planner.database.lesson_repository import (
    SqlAlchemyLessonRepository,
)
from schedule_planner.database.unit_of_work import SqlAlchemyUnitOfWork
from schedule_planner.schedule_service import ScheduleService


def get_unit_of_work() -> Iterator[SqlAlchemyUnitOfWork]:
    """Предоставляет Unit of Work для HTTP-запроса."""
    with SqlAlchemyUnitOfWork(create_session) as unit_of_work:
        yield unit_of_work


UnitOfWorkDep = Annotated[
    SqlAlchemyUnitOfWork,
    Depends(get_unit_of_work),
]


def get_catalog_service(
    unit_of_work: UnitOfWorkDep,
) -> CatalogService:
    """Создаёт сервис справочников с общей сессией."""
    session = unit_of_work.session
    lesson_repository = SqlAlchemyLessonRepository(session)

    return CatalogService(
        teacher_repo=SqlAlchemyTeacherRepository(session),
        group_repo=SqlAlchemyGroupRepository(session),
        subject_repo=SqlAlchemySubjectRepository(session),
        classroom_repo=SqlAlchemyClassroomRepository(session),
        usage_checker=CatalogUsageChecker(lesson_repository),
    )


def get_schedule_service(
    unit_of_work: UnitOfWorkDep,
) -> ScheduleService:
    """Создаёт сервис расписания с общей сессией."""
    return ScheduleService(
        SqlAlchemyLessonRepository(unit_of_work.session),
        LessonConflictChain(),
    )


CatalogServiceDep = Annotated[
    CatalogService,
    Depends(get_catalog_service),
]

ScheduleServiceDep = Annotated[
    ScheduleService,
    Depends(get_schedule_service),
]
