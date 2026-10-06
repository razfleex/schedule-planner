from collections.abc import Callable
from datetime import time

from schedule_planner.catalog_service import CatalogService
from schedule_planner.models import Lesson, Weekday
from schedule_planner.schedule_service import ScheduleService


class LessonManagementCli:
    """Управляет учебными занятиями через терминальный интерфейс."""

    def __init__(
        self,
        schedule_service: ScheduleService,
        catalog_service: CatalogService,
        input_func: Callable[[str], str] = input,
        output: Callable[[str], None] = print,
    ) -> None:
        """Создаёт CLI с сервисами расписания и каталога."""
        self._schedule_service = schedule_service
        self._catalog_service = catalog_service
        self._input = input_func
        self._output = output

    def create_lesson(self) -> None:
        """Создаёт новое занятие по данным пользователя."""
        try:
            lesson_id = self._read_int("ID занятия: ")
            lesson = self._read_lesson(lesson_id)
            self._schedule_service.create_lesson(lesson)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return

        self._output(f"Занятие {lesson_id} создано.")

    def update_lesson(self) -> None:
        """Изменяет существующее занятие по данным пользователя."""
        try:
            lesson_id = self._read_int("ID изменяемого занятия: ")
            lesson = self._read_lesson(lesson_id)
            self._schedule_service.update_lesson(lesson)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return

        self._output(f"Занятие {lesson_id} изменено.")

    def delete_lesson(self) -> None:
        """Удаляет существующее занятие."""
        try:
            lesson_id = self._read_int("ID удаляемого занятия: ")
            self._schedule_service.delete_lesson(lesson_id)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return

        self._output(f"Занятие {lesson_id} удалено.")

    def _read_lesson(self, lesson_id: int) -> Lesson:
        """Считывает данные занятия и создаёт объект Lesson."""
        teacher_id = self._read_int("ID преподавателя: ")
        teacher = self._catalog_service.get_teacher_by_id(teacher_id)

        if teacher is None:
            raise ValueError(
                f"Преподаватель с идентификатором {teacher_id} не найден."
            )

        group_id = self._read_int("ID учебной группы: ")
        group = self._catalog_service.get_group_by_id(group_id)

        if group is None:
            raise ValueError(
                f"Учебная группа с идентификатором {group_id} не найдена."
            )

        subject_id = self._read_int("ID дисциплины: ")
        subject = self._catalog_service.get_subject_by_id(subject_id)

        if subject is None:
            raise ValueError(
                f"Дисциплина с идентификатором {subject_id} не найдена."
            )

        classroom_id = self._read_int("ID аудитории: ")
        classroom = self._catalog_service.get_classroom_by_id(classroom_id)

        if classroom is None:
            raise ValueError(
                f"Аудитория с идентификатором {classroom_id} не найдена."
            )

        day = self._read_weekday()
        start_time = self._read_time("Время начала (ЧЧ:ММ): ")
        end_time = self._read_time("Время окончания (ЧЧ:ММ): ")

        return Lesson(
            id=lesson_id,
            teacher=teacher,
            group=group,
            subject=subject,
            classroom=classroom,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
        )

    def _read_int(self, prompt: str) -> int:
        """Считывает целое число."""
        value = self._input(prompt)

        try:
            return int(value)
        except ValueError as error:
            raise ValueError(
                "Идентификатор должен быть целым числом."
            ) from error

    def _read_weekday(self) -> Weekday:
        """Считывает день недели по его номеру."""
        self._output(
            "Дни недели: "
            "1 — Понедельник, 2 — Вторник, 3 — Среда, "
            "4 — Четверг, 5 — Пятница, 6 — Суббота, "
            "7 — Воскресенье."
        )

        day_number = self._read_int("Номер дня недели: ")
        weekdays = list(Weekday)

        if day_number < 1 or day_number > len(weekdays):
            raise ValueError("Номер дня недели должен быть от 1 до 7.")

        return weekdays[day_number - 1]
    
    
    def _read_time(self, prompt: str) -> time:
        """Считывает время в формате ЧЧ:ММ."""
        value = self._input(prompt)

        try:
            return time.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                "Время должно быть указано в формате ЧЧ:ММ."
            ) from error