from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status

from schedule_planner.dependencies import CatalogServiceDep, UnitOfWorkDep
from schedule_planner.dtos.requests import GroupRequest
from schedule_planner.dtos.responses import GroupResponse
from schedule_planner.models import Group

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
)

GroupId = Annotated[int, Path(gt=0)]


@router.get("", response_model=list[GroupResponse])
def get_groups(
    service: CatalogServiceDep,
) -> list[GroupResponse]:
    """Возвращает список учебных групп."""
    return [GroupResponse.model_validate(group) for group in service.get_all_groups()]


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: GroupId,
    service: CatalogServiceDep,
) -> GroupResponse:
    """Возвращает группу по идентификатору."""
    group = service.get_group_by_id(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная группа не найдена.",
        )

    return GroupResponse.model_validate(group)


@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_group(
    request: GroupRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> GroupResponse:
    """Добавляет учебную группу."""
    try:
        group = service.add_group(Group(request.id, request.name))
        response = GroupResponse.model_validate(group)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: GroupId,
    request: GroupRequest,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> GroupResponse:
    """Обновляет данные учебной группы."""
    if group_id != request.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Идентификаторы должны совпадать.",
        )

    if service.get_group_by_id(group_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная группа не найдена.",
        )

    try:
        group = service.update_group(Group(group_id, request.name))
        response = GroupResponse.model_validate(group)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return response


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_group(
    group_id: GroupId,
    service: CatalogServiceDep,
    unit_of_work: UnitOfWorkDep,
) -> Response:
    """Удаляет учебную группу."""
    if service.get_group_by_id(group_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учебная группа не найдена.",
        )

    try:
        service.delete_group(group_id)
        unit_of_work.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
