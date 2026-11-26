from datetime import time
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    PositiveInt,
    StringConstraints,
    model_validator,
)

from schedule_planner.models import Weekday

RequiredText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class TeacherRequest(BaseModel):
    """Запрос на создание или изменение преподавателя."""

    id: PositiveInt
    full_name: RequiredText


class GroupRequest(BaseModel):
    """Запрос на создание или изменение учебной группы."""

    id: PositiveInt
    name: RequiredText


class SubjectRequest(BaseModel):
    """Запрос на создание или изменение дисциплины."""

    id: PositiveInt
    name: RequiredText


class ClassroomRequest(BaseModel):
    """Запрос на создание или изменение аудитории."""

    id: PositiveInt
    name: RequiredText


class LessonRequest(BaseModel):
    """Запрос на создание или изменение учебного занятия."""

    id: PositiveInt
    teacher_id: PositiveInt
    group_id: PositiveInt
    subject_id: PositiveInt
    classroom_id: PositiveInt
    day_of_week: Weekday
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        """Проверяет корректность времени занятия."""
        if self.end_time <= self.start_time:
            raise ValueError(
                "Время окончания занятия должно быть позже времени начала."
            )
        return self
