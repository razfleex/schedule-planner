from collections.abc import Callable

from schedule_planner.models import Lesson, Weekday
from schedule_planner.schedule_service import ScheduleService


class ScheduleCli:
    """Отображает учебное расписание в терминале."""

    def __init__(
        self,
        schedule_service: ScheduleService,
        output: Callable[[str], None] = print,
    ) -> None:
        """Создаёт CLI с сервисом расписания и функцией вывода."""
        self._schedule_service = schedule_service
        self._output = output

    def show_all_lessons(self) -> None:
        """Показывает всё расписание для Составителя."""
        self._show_lessons(
            self._schedule_service.get_all_lessons(),
            "Полное расписание",
        )

    def show_lessons_by_group(self, group_id: int) -> None:
        """Показывает занятия выбранной учебной группы."""
        self._show_lessons(
            self._schedule_service.get_lessons_by_group(group_id),
            "Расписание учебной группы",
        )

    def show_lessons_by_teacher(self, teacher_id: int) -> None:
        """Показывает занятия выбранного преподавателя."""
        self._show_lessons(
            self._schedule_service.get_lessons_by_teacher(teacher_id),
            "Расписание преподавателя",
        )

    def show_lessons_by_classroom(self, classroom_id: int) -> None:
        """Показывает занятия выбранной аудитории."""
        self._show_lessons(
            self._schedule_service.get_lessons_by_classroom(classroom_id),
            "Расписание аудитории",
        )

    def show_lessons_by_day(self, day: Weekday) -> None:
        """Показывает занятия выбранного дня недели."""
        self._show_lessons(
            self._schedule_service.get_lessons_by_day(day),
            f"Расписание: {day.value}",
        )

    def show_student_schedule(self, group_id: int) -> None:
        """Показывает Студенту расписание его учебной группы."""
        self._show_lessons(
            self._schedule_service.get_lessons_by_group(group_id),
            "Расписание Студента",
        )

    def show_teacher_schedule(self, teacher_id: int) -> None:
        """Показывает Преподавателю связанные с ним занятия."""
        self._show_lessons(
            self._schedule_service.get_lessons_by_teacher(teacher_id),
            "Расписание Преподавателя",
        )

    def _show_lessons(
        self,
        lessons: list[Lesson],
        title: str,
    ) -> None:
        """Выводит заголовок и список занятий."""
        self._output(title)

        if not lessons:
            self._output("Занятий нет.")
            return

        for lesson in lessons:
            self._output(self._format_lesson(lesson))

    def _format_lesson(self, lesson: Lesson) -> str:
        """Форматирует занятие для отображения в терминале."""
        start_time = lesson.start_time.strftime("%H:%M")
        end_time = lesson.end_time.strftime("%H:%M")

        return (
            f"[{lesson.id}] "
            f"{lesson.day_of_week.value} "
            f"{start_time}–{end_time} | "
            f"{lesson.group.name} | "
            f"{lesson.subject.name} | "
            f"{lesson.teacher.full_name} | "
            f"{lesson.classroom.name}"
        )