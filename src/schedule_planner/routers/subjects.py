from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from schedule_planner.dependencies import CatalogServiceDep, UnitOfWorkDep
from schedule_planner.dtos.requests import SubjectRequest
from schedule_planner.dtos.responses import SubjectResponse
from schedule_planner.models import Subject

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
)

SubjectId = Annotated[int, Path(gt=0)]


@router.get("", response_model=list[SubjectResponse])
def get_subjects(
    service: CatalogServiceDep,
) -> list[SubjectResponse]:
    """Возвращает список учебных дисциплин."""
    return [
        SubjectResponse.model_validate(subject)
        for subject in service.get_all_subjects()
    ]


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: SubjectId,
    service: CatalogServiceDep,
) -> SubjectResponse:
    """Возвращает дисциплину по идентификатору."""
    subject = service.get_subject_by_id(subject_id)

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная дисциплина не найдена.",
        )

    return SubjectResponse.model_validate(subject)


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subject(
    request: SubjectRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> SubjectResponse:
    """Добавляет учебную дисциплину."""
    try:
        subject = service.add_subject(Subject(request.id, request.name))
        response = SubjectResponse.model_validate(subject)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: SubjectId,
    request: SubjectRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> SubjectResponse:
    """Обновляет данные учебной дисциплины."""
    if subject_id != request.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Идентификаторы должны совпадать.",
        )

    if service.get_subject_by_id(subject_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная дисциплина не найдена.",
        )

    try:
        subject = service.update_subject(Subject(subject_id, request.name))
        response = SubjectResponse.model_validate(subject)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subject(
    subject_id: SubjectId,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> Response:
    """Удаляет учебную дисциплину."""
    if service.get_subject_by_id(subject_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная дисциплина не найдена.",
        )

    try:
        service.delete_subject(subject_id)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
