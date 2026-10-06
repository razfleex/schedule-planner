from schedule_planner.conflicts import ConflictChecker
from schedule_planner.lesson_repository import LessonRepository
from schedule_planner.models import Lesson, Weekday


class ScheduleService:
    """Управляет учебными занятиями и применяет правила расписания."""

    def __init__(
        self,
        repository: LessonRepository,
        conflict_checker: ConflictChecker,
    ) -> None:
        """Создаёт сервис с хранилищем и проверкой конфликтов."""
        self._repository = repository
        self._conflict_checker = conflict_checker

    def create_lesson(self, lesson: Lesson) -> None:
        """Создаёт занятие после проверки идентификатора и конфликтов."""
        if self._repository.get_by_id(lesson.id) is not None:
            raise ValueError(
                f"Занятие с идентификатором {lesson.id} уже существует."
            )

        self._conflict_checker.check(
            lesson,
            self._repository.get_all(),
        )
        self._repository.add(lesson)

    def get_lesson(self, lesson_id: int) -> Lesson | None:
        """Возвращает занятие по идентификатору."""
        return self._repository.get_by_id(lesson_id)

    def get_all_lessons(self) -> list[Lesson]:
        """Возвращает все занятия."""
        return self._repository.get_all()

    def update_lesson(self, lesson: Lesson) -> None:
        """Изменяет занятие после проверки существования и конфликтов."""
        if self._repository.get_by_id(lesson.id) is None:
            raise ValueError(
                f"Занятие с идентификатором {lesson.id} не найдено."
            )

        self._conflict_checker.check(
            lesson,
            self._repository.get_all(),
            exclude_lesson_id=lesson.id,
        )
        self._repository.update(lesson)

    def delete_lesson(self, lesson_id: int) -> None:
        """Удаляет занятие."""
        self._repository.delete(lesson_id)

    def get_lessons_by_teacher(self, teacher_id: int) -> list[Lesson]:
        """Возвращает занятия выбранного преподавателя."""
        return [
            lesson
            for lesson in self._repository.get_all()
            if lesson.teacher.id == teacher_id
        ]

    def get_lessons_by_group(self, group_id: int) -> list[Lesson]:
        """Возвращает занятия выбранной учебной группы."""
        return [
            lesson
            for lesson in self._repository.get_all()
            if lesson.group.id == group_id
        ]

    def get_lessons_by_classroom(self, classroom_id: int) -> list[Lesson]:
        """Возвращает занятия выбранной аудитории."""
        return [
            lesson
            for lesson in self._repository.get_all()
            if lesson.classroom.id == classroom_id
        ]

    def get_lessons_by_day(self, day: Weekday) -> list[Lesson]:
        """Возвращает занятия выбранного дня недели."""
        return [
            lesson
            for lesson in self._repository.get_all()
            if lesson.day_of_week == day
        ]