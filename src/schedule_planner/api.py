from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Response, status

from schedule_planner.dependencies import CatalogServiceDep, UnitOfWorkDep
from schedule_planner.dtos.requests import TeacherRequest
from schedule_planner.dtos.responses import TeacherResponse
from schedule_planner.models import Teacher

app = FastAPI(
    title="Schedule Planner",
    description="API для планирования учебных занятий и расписаний",
    version="0.1.0",
)

TeacherId = Annotated[int, Path(gt=0)]


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Проверяет доступность API."""
    return {"status": "ok"}


@app.get(
    "/teachers",
    response_model=list[TeacherResponse],
    tags=["Teachers"],
)
def get_teachers(
    service: CatalogServiceDep,
) -> list[TeacherResponse]:
    """Возвращает список преподавателей."""
    return [
        TeacherResponse.model_validate(teacher)
        for teacher in service.get_all_teachers()
    ]


@app.get(
    "/teachers/{teacher_id}",
    response_model=TeacherResponse,
    tags=["Teachers"],
)
def get_teacher(
    teacher_id: TeacherId,
    service: CatalogServiceDep,
) -> TeacherResponse:
    """Возвращает преподавателя по идентификатору."""
    teacher = service.get_teacher_by_id(teacher_id)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден.",
        )

    return TeacherResponse.model_validate(teacher)


@app.post(
    "/teachers",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Teachers"],
)
def create_teacher(
    request: TeacherRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> TeacherResponse:
    """Добавляет преподавателя."""
    try:
        teacher = service.add_teacher(Teacher(request.id, request.full_name))
        response = TeacherResponse.model_validate(teacher)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@app.put(
    "/teachers/{teacher_id}",
    response_model=TeacherResponse,
    tags=["Teachers"],
)
def update_teacher(
    teacher_id: TeacherId,
    request: TeacherRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> TeacherResponse:
    """Обновляет данные преподавателя."""
    if teacher_id != request.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Идентификаторы должны совпадать.",
        )

    if service.get_teacher_by_id(teacher_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден.",
        )

    try:
        teacher = service.update_teacher(Teacher(teacher_id, request.full_name))
        response = TeacherResponse.model_validate(teacher)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@app.delete(
    "/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Teachers"],
)
def delete_teacher(
    teacher_id: TeacherId,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> Response:
    """Удаляет преподавателя."""
    if service.get_teacher_by_id(teacher_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден.",
        )

    try:
        service.delete_teacher(teacher_id)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
