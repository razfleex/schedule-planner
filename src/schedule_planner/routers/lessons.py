from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response, status

from schedule_planner.dependencies import (
    CatalogServiceDep,
    ScheduleServiceDep,
    UnitOfWorkDep,
)
from schedule_planner.dtos.requests import LessonRequest
from schedule_planner.dtos.responses import LessonResponse
from schedule_planner.models import Lesson, Weekday

router = APIRouter(
    prefix="/lessons",
    tags=["Lessons"],
)

LessonId = Annotated[int, Path(gt=0)]
FilterId = Annotated[int | None, Query(gt=0)]


def build_lesson(
    request: LessonRequest,
    catalog: CatalogServiceDep,
) -> Lesson:
    """Создаёт доменный объект занятия из входящего DTO."""
    teacher = catalog.get_teacher_by_id(request.teacher_id)
    group = catalog.get_group_by_id(request.group_id)
    subject = catalog.get_subject_by_id(request.subject_id)
    classroom = catalog.get_classroom_by_id(request.classroom_id)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден.",
        )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная группа не найдена.",
        )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная дисциплина не найдена.",
        )

    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аудитория не найдена.",
        )

    return Lesson(
        id=request.id,
        teacher=teacher,
        group=group,
        subject=subject,
        classroom=classroom,
        day_of_week=request.day_of_week,
        start_time=request.start_time,
        end_time=request.end_time,
    )


@router.get("", response_model=list[LessonResponse])
def get_lessons(
    service: ScheduleServiceDep,
    teacher_id: FilterId = None,
    group_id: FilterId = None,
    classroom_id: FilterId = None,
    day_of_week: Weekday | None = None,
) -> list[LessonResponse]:
    """Возвращает занятия с учётом заданных фильтров."""
    lessons = service.get_all_lessons()

    if teacher_id is not None:
        lessons = [lesson for lesson in lessons if lesson.teacher.id == teacher_id]

    if group_id is not None:
        lessons = [lesson for lesson in lessons if lesson.group.id == group_id]

    if classroom_id is not None:
        lessons = [lesson for lesson in lessons if lesson.classroom.id == classroom_id]

    if day_of_week is not None:
        lessons = [lesson for lesson in lessons if lesson.day_of_week == day_of_week]

    return [LessonResponse.model_validate(lesson) for lesson in lessons]


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: LessonId,
    service: ScheduleServiceDep,
) -> LessonResponse:
    """Возвращает занятие по идентификатору."""
    lesson = service.get_lesson(lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебное занятие не найдено.",
        )

    return LessonResponse.model_validate(lesson)


@router.post(
    "",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    request: LessonRequest,
    catalog: CatalogServiceDep,
    service: ScheduleServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> LessonResponse:
    """Создаёт учебное занятие."""
    try:
        lesson = build_lesson(request, catalog)
        service.create_lesson(lesson)
        response = LessonResponse.model_validate(lesson)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: LessonId,
    request: LessonRequest,
    catalog: CatalogServiceDep,
    service: ScheduleServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> LessonResponse:
    """Обновляет учебное занятие."""
    if lesson_id != request.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Идентификаторы должны совпадать.",
        )

    if service.get_lesson(lesson_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебное занятие не найдено.",
        )

    try:
        lesson = build_lesson(request, catalog)
        service.update_lesson(lesson)
        response = LessonResponse.model_validate(lesson)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.delete(
    "/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lesson(
    lesson_id: LessonId,
    service: ScheduleServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> Response:
    """Удаляет учебное занятие."""
    if service.get_lesson(lesson_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебное занятие не найдено.",
        )

    try:
        service.delete_lesson(lesson_id)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
