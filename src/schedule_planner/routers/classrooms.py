from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from schedule_planner.dependencies import CatalogServiceDep, UnitOfWorkDep
from schedule_planner.dtos.requests import ClassroomRequest
from schedule_planner.dtos.responses import ClassroomResponse
from schedule_planner.models import Classroom

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"],
)

ClassroomId = Annotated[int, Path(gt=0)]


@router.get("", response_model=list[ClassroomResponse])
def get_classrooms(
    service: CatalogServiceDep,
) -> list[ClassroomResponse]:
    """Возвращает список аудиторий."""
    return [
        ClassroomResponse.model_validate(classroom)
        for classroom in service.get_all_classrooms()
    ]


@router.get("/{classroom_id}", response_model=ClassroomResponse)
def get_classroom(
    classroom_id: ClassroomId,
    service: CatalogServiceDep,
) -> ClassroomResponse:
    """Возвращает аудиторию по идентификатору."""
    classroom = service.get_classroom_by_id(classroom_id)

    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аудитория не найдена.",
        )

    return ClassroomResponse.model_validate(classroom)


@router.post(
    "",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_classroom(
    request: ClassroomRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> ClassroomResponse:
    """Добавляет аудиторию."""
    try:
        classroom = service.add_classroom(Classroom(request.id, request.name))
        response = ClassroomResponse.model_validate(classroom)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.put("/{classroom_id}", response_model=ClassroomResponse)
def update_classroom(
    classroom_id: ClassroomId,
    request: ClassroomRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> ClassroomResponse:
    """Обновляет данные аудитории."""
    if classroom_id != request.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Идентификаторы должны совпадать.",
        )

    if service.get_classroom_by_id(classroom_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аудитория не найдена.",
        )

    try:
        classroom = service.update_classroom(Classroom(classroom_id, request.name))
        response = ClassroomResponse.model_validate(classroom)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.delete(
    "/{classroom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_classroom(
    classroom_id: ClassroomId,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> Response:
    """Удаляет аудиторию."""
    if service.get_classroom_by_id(classroom_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аудитория не найдена.",
        )

    try:
        service.delete_classroom(classroom_id)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
