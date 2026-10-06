from typing import Protocol

from schedule_planner.models import Lesson


class LessonRepository(Protocol):
    """Определяет операции хранения учебных занятий."""

    def add(self, lesson: Lesson) -> None:
        """Добавляет новое занятие."""
        ...

    def get_by_id(self, lesson_id: int) -> Lesson | None:
        """Возвращает занятие по идентификатору."""
        ...

    def get_all(self) -> list[Lesson]:
        """Возвращает все сохранённые занятия."""
        ...

    def update(self, lesson: Lesson) -> None:
        """Обновляет существующее занятие."""
        ...

    def delete(self, lesson_id: int) -> None:
        """Удаляет занятие по идентификатору."""
        ...


class InMemoryLessonRepository:
    """Хранит учебные занятия в памяти во время работы программы."""

    def __init__(self) -> None:
        """Создаёт пустое хранилище занятий."""
        self._lessons: dict[int, Lesson] = {}

    def add(self, lesson: Lesson) -> None:
        """Добавляет занятие, если его идентификатор ещё не используется."""
        if lesson.id in self._lessons:
            raise ValueError(
                f"Занятие с идентификатором {lesson.id} уже существует."
            )

        self._lessons[lesson.id] = lesson

    def get_by_id(self, lesson_id: int) -> Lesson | None:
        """Возвращает занятие по идентификатору или None."""
        return self._lessons.get(lesson_id)

    def get_all(self) -> list[Lesson]:
        """Возвращает список всех сохранённых занятий."""
        return list(self._lessons.values())

    def update(self, lesson: Lesson) -> None:
        """Заменяет данные существующего занятия."""
        if lesson.id not in self._lessons:
            raise ValueError(
                f"Занятие с идентификатором {lesson.id} не найдено."
            )

        self._lessons[lesson.id] = lesson

    def delete(self, lesson_id: int) -> None:
        """Удаляет существующее занятие."""
        if lesson_id not in self._lessons:
            raise ValueError(
                f"Занятие с идентификатором {lesson_id} не найдено."
            )

        del self._lessons[lesson_id]