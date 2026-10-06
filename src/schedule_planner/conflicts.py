from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Protocol

from schedule_planner.models import Lesson


class ScheduleConflictError(ValueError):
    """Сообщает о временном конфликте учебных занятий."""


class ConflictChecker(Protocol):
    """Определяет интерфейс проверки занятия на конфликты."""

    def check(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None = None,
    ) -> None:
        """Проверяет занятие относительно существующего расписания."""
        ...


def _lessons_overlap(first: Lesson, second: Lesson) -> bool:
    """Проверяет пересечение двух занятий по дню и времени."""
    if first.day_of_week != second.day_of_week:
        return False

    return (
        first.start_time < second.end_time
        and second.start_time < first.end_time
    )


class ConflictHandler(ABC):
    """Базовый обработчик цепочки проверок конфликтов."""

    def __init__(self) -> None:
        """Создаёт обработчик без следующего элемента цепочки."""
        self._next_handler: ConflictHandler | None = None

    def set_next(self, handler: ConflictHandler) -> ConflictHandler:
        """Добавляет следующий обработчик в цепочку."""
        self._next_handler = handler
        return handler

    def check(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None = None,
    ) -> None:
        """Передаёт проверку следующему обработчику."""
        if self._next_handler is not None:
            self._next_handler.check(
                lesson,
                existing_lessons,
                exclude_lesson_id,
            )

    @abstractmethod
    def _matches(self, lesson: Lesson, existing: Lesson) -> bool:
        """Определяет наличие конфликта конкретного типа."""

    @abstractmethod
    def _message(self, existing: Lesson) -> str:
        """Возвращает описание обнаруженного конфликта."""

    def _check_current_rule(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None,
    ) -> None:
        """Проверяет занятие по правилу текущего обработчика."""
        for existing in existing_lessons:
            if existing.id == exclude_lesson_id:
                continue

            if not _lessons_overlap(lesson, existing):
                continue

            if self._matches(lesson, existing):
                raise ScheduleConflictError(self._message(existing))


class TeacherConflictHandler(ConflictHandler):
    """Проверяет занятость преподавателя."""

    def check(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None = None,
    ) -> None:
        """Проверяет конфликт преподавателя и продолжает цепочку."""
        lessons = tuple(existing_lessons)
        self._check_current_rule(lesson, lessons, exclude_lesson_id)
        super().check(lesson, lessons, exclude_lesson_id)

    def _matches(self, lesson: Lesson, existing: Lesson) -> bool:
        """Сравнивает преподавателей двух занятий."""
        return lesson.teacher.id == existing.teacher.id

    def _message(self, existing: Lesson) -> str:
        """Возвращает причину конфликта преподавателя."""
        return (
            "Конфликт преподавателя: "
            f"{existing.teacher.full_name} уже занят в это время."
        )


class GroupConflictHandler(ConflictHandler):
    """Проверяет занятость учебной группы."""

    def check(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None = None,
    ) -> None:
        """Проверяет конфликт группы и продолжает цепочку."""
        lessons = tuple(existing_lessons)
        self._check_current_rule(lesson, lessons, exclude_lesson_id)
        super().check(lesson, lessons, exclude_lesson_id)

    def _matches(self, lesson: Lesson, existing: Lesson) -> bool:
        """Сравнивает группы двух занятий."""
        return lesson.group.id == existing.group.id

    def _message(self, existing: Lesson) -> str:
        """Возвращает причину конфликта учебной группы."""
        return (
            "Конфликт учебной группы: "
            f"{existing.group.name} уже занята в это время."
        )


class ClassroomConflictHandler(ConflictHandler):
    """Проверяет занятость аудитории."""

    def check(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None = None,
    ) -> None:
        """Проверяет конфликт аудитории и продолжает цепочку."""
        lessons = tuple(existing_lessons)
        self._check_current_rule(lesson, lessons, exclude_lesson_id)
        super().check(lesson, lessons, exclude_lesson_id)

    def _matches(self, lesson: Lesson, existing: Lesson) -> bool:
        """Сравнивает аудитории двух занятий."""
        return lesson.classroom.id == existing.classroom.id

    def _message(self, existing: Lesson) -> str:
        """Возвращает причину конфликта аудитории."""
        return (
            "Конфликт аудитории: "
            f"{existing.classroom.name} уже занята в это время."
        )


class LessonConflictChain:
    """Проверяет занятие цепочкой правил временных конфликтов."""

    def __init__(self) -> None:
        """Создаёт цепочку проверок преподавателя, группы и аудитории."""
        teacher_handler = TeacherConflictHandler()
        group_handler = GroupConflictHandler()
        classroom_handler = ClassroomConflictHandler()

        teacher_handler.set_next(group_handler).set_next(classroom_handler)

        self._first_handler = teacher_handler

    def check(
        self,
        lesson: Lesson,
        existing_lessons: Iterable[Lesson],
        exclude_lesson_id: int | None = None,
    ) -> None:
        """Запускает последовательную проверку всех конфликтов."""
        self._first_handler.check(
            lesson,
            existing_lessons,
            exclude_lesson_id,
        )