from dataclasses import dataclass
from datetime import time
from enum import Enum


class Weekday(str, Enum):
    """Представляет день типовой учебной недели."""

    MONDAY = "Понедельник"
    TUESDAY = "Вторник"
    WEDNESDAY = "Среда"
    THURSDAY = "Четверг"
    FRIDAY = "Пятница"
    SATURDAY = "Суббота"
    SUNDAY = "Воскресенье"


def _validate_id(identifier: int) -> None:
    """Проверяет корректность уникального идентификатора сущности."""
    if identifier <= 0:
        raise ValueError("Идентификатор должен быть положительным числом.")


def _normalize_required_text(value: str, field_name: str) -> str:
    """Проверяет обязательное текстовое поле и удаляет лишние пробелы."""
    normalized_value = value.strip()

    if not normalized_value:
        raise ValueError(f"Поле «{field_name}» не должно быть пустым.")

    return normalized_value


@dataclass
class Teacher:
    """Представляет преподавателя."""

    id: int
    full_name: str

    def __post_init__(self) -> None:
        """Проверяет данные преподавателя после создания объекта."""
        _validate_id(self.id)
        self.full_name = _normalize_required_text(self.full_name, "ФИО")


@dataclass
class Group:
    """Представляет учебную группу."""

    id: int
    name: str

    def __post_init__(self) -> None:
        """Проверяет данные учебной группы после создания объекта."""
        _validate_id(self.id)
        self.name = _normalize_required_text(self.name, "Наименование группы")


@dataclass
class Subject:
    """Представляет учебную дисциплину."""

    id: int
    name: str

    def __post_init__(self) -> None:
        """Проверяет данные дисциплины после создания объекта."""
        _validate_id(self.id)
        self.name = _normalize_required_text(self.name, "Наименование дисциплины")


@dataclass
class Classroom:
    """Представляет аудиторию."""

    id: int
    name: str

    def __post_init__(self) -> None:
        """Проверяет данные аудитории после создания объекта."""
        _validate_id(self.id)
        self.name = _normalize_required_text(self.name, "Обозначение аудитории")


@dataclass
class Lesson:
    """Представляет учебное занятие."""

    id: int
    teacher: Teacher
    group: Group
    subject: Subject
    classroom: Classroom
    day_of_week: Weekday
    start_time: time
    end_time: time

    def __post_init__(self) -> None:
        """Проверяет основные данные занятия после создания объекта."""
        _validate_id(self.id)

        if self.end_time <= self.start_time:
            raise ValueError(
                "Время окончания занятия должно быть позже времени начала."
            )