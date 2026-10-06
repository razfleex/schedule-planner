from schedule_planner.lesson_repository import LessonRepository


class CatalogEntityInUseError(ValueError):
    """Сообщает, что справочная сущность используется в занятии."""


class CatalogUsageChecker:
    """Проверяет использование справочных сущностей в расписании."""

    def __init__(self, lesson_repository: LessonRepository) -> None:
        """Создаёт проверяющий объект с хранилищем занятий."""
        self._lesson_repository = lesson_repository

    def ensure_teacher_not_used(self, teacher_id: int) -> None:
        """Запрещает удаление используемого преподавателя."""
        for lesson in self._lesson_repository.get_all():
            if lesson.teacher.id == teacher_id:
                raise CatalogEntityInUseError(
                    "Нельзя удалить преподавателя: "
                    "он используется в существующем занятии."
                )

    def ensure_group_not_used(self, group_id: int) -> None:
        """Запрещает удаление используемой учебной группы."""
        for lesson in self._lesson_repository.get_all():
            if lesson.group.id == group_id:
                raise CatalogEntityInUseError(
                    "Нельзя удалить учебную группу: "
                    "она используется в существующем занятии."
                )

    def ensure_subject_not_used(self, subject_id: int) -> None:
        """Запрещает удаление используемой дисциплины."""
        for lesson in self._lesson_repository.get_all():
            if lesson.subject.id == subject_id:
                raise CatalogEntityInUseError(
                    "Нельзя удалить дисциплину: "
                    "она используется в существующем занятии."
                )

    def ensure_classroom_not_used(self, classroom_id: int) -> None:
        """Запрещает удаление используемой аудитории."""
        for lesson in self._lesson_repository.get_all():
            if lesson.classroom.id == classroom_id:
                raise CatalogEntityInUseError(
                    "Нельзя удалить аудиторию: "
                    "она используется в существующем занятии."
                )