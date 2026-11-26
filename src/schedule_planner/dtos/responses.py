from datetime import time

from pydantic import BaseModel, ConfigDict

from schedule_planner.models import Weekday


class TeacherResponse(BaseModel):
    """Данные преподавателя."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str


class GroupResponse(BaseModel):
    """Данные учебной группы."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SubjectResponse(BaseModel):
    """Данные учебной дисциплины."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ClassroomResponse(BaseModel):
    """Данные аудитории."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class LessonResponse(BaseModel):
    """Данные учебного занятия."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher: TeacherResponse
    group: GroupResponse
    subject: SubjectResponse
    classroom: ClassroomResponse
    day_of_week: Weekday
    start_time: time
    end_time: time
