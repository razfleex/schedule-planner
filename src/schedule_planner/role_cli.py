from collections.abc import Callable

from schedule_planner.catalog_cli import CatalogCli
from schedule_planner.lesson_management_cli import LessonManagementCli
from schedule_planner.models import Weekday
from schedule_planner.schedule_cli import ScheduleCli


class RoleCli:
    """Управляет терминальными меню ролей пользователей."""

    def __init__(
        self,
        schedule_cli: ScheduleCli,
        lesson_management_cli: LessonManagementCli,
        catalog_cli: CatalogCli,
        input_func: Callable[[str], str] = input,
        output: Callable[[str], None] = print,
    ) -> None:
        """Создаёт меню ролей с необходимыми CLI-компонентами."""
        self._schedule_cli = schedule_cli
        self._lesson_management_cli = lesson_management_cli
        self._catalog_cli = catalog_cli
        self._input = input_func
        self._output = output

    def run(self) -> None:
        """Запускает главное меню выбора роли."""
        while True:
            self._output(
                "\nВыберите роль:\n"
                "1 — Составитель\n"
                "2 — Студент\n"
                "3 — Преподаватель\n"
                "0 — Выход"
            )
            choice = self._input("Выбор: ")

            if choice == "1":
                self._run_compiler_menu()
            elif choice == "2":
                self._run_student_menu()
            elif choice == "3":
                self._run_teacher_menu()
            elif choice == "0":
                self._output("Работа программы завершена.")
                return
            else:
                self._output("Ошибка: неизвестный пункт меню.")

    def _run_compiler_menu(self) -> None:
        """Запускает меню Составителя."""
        while True:
            self._output(
                "\nМеню Составителя:\n"
                "1 — Показать всё расписание\n"
                "2 — Расписание учебной группы\n"
                "3 — Расписание преподавателя\n"
                "4 — Расписание аудитории\n"
                "5 — Расписание дня недели\n"
                "6 — Создать занятие\n"
                "7 — Изменить занятие\n"
                "8 — Удалить занятие\n"
                "9 — Управление справочниками\n"
                "0 — Назад"
            )
            choice = self._input("Выбор: ")

            if choice == "1":
                self._schedule_cli.show_all_lessons()
            elif choice == "2":
                group_id = self._read_id("ID учебной группы: ")
                if group_id is not None:
                    self._schedule_cli.show_lessons_by_group(group_id)
            elif choice == "3":
                teacher_id = self._read_id("ID преподавателя: ")
                if teacher_id is not None:
                    self._schedule_cli.show_lessons_by_teacher(teacher_id)
            elif choice == "4":
                classroom_id = self._read_id("ID аудитории: ")
                if classroom_id is not None:
                    self._schedule_cli.show_lessons_by_classroom(classroom_id)
            elif choice == "5":
                day = self._read_weekday()
                if day is not None:
                    self._schedule_cli.show_lessons_by_day(day)
            elif choice == "6":
                self._lesson_management_cli.create_lesson()
            elif choice == "7":
                self._lesson_management_cli.update_lesson()
            elif choice == "8":
                self._lesson_management_cli.delete_lesson()
            elif choice == "9":
                self._run_catalog_menu()
            elif choice == "0":
                return
            else:
                self._output("Ошибка: неизвестный пункт меню.")

    def _run_catalog_menu(self) -> None:
        """Позволяет Составителю выбрать справочник для редактирования."""
        catalogs = {
            "1": (
                "Преподаватели",
                self._catalog_cli.show_teachers,
                self._catalog_cli.add_teacher,
                self._catalog_cli.update_teacher,
                self._catalog_cli.delete_teacher,
            ),
            "2": (
                "Учебные группы",
                self._catalog_cli.show_groups,
                self._catalog_cli.add_group,
                self._catalog_cli.update_group,
                self._catalog_cli.delete_group,
            ),
            "3": (
                "Дисциплины",
                self._catalog_cli.show_subjects,
                self._catalog_cli.add_subject,
                self._catalog_cli.update_subject,
                self._catalog_cli.delete_subject,
            ),
            "4": (
                "Аудитории",
                self._catalog_cli.show_classrooms,
                self._catalog_cli.add_classroom,
                self._catalog_cli.update_classroom,
                self._catalog_cli.delete_classroom,
            ),
        }

        while True:
            self._output(
                "\nУправление справочниками:\n"
                "1 — Преподаватели\n"
                "2 — Учебные группы\n"
                "3 — Дисциплины\n"
                "4 — Аудитории\n"
                "0 — Назад"
            )
            choice = self._input("Выбор: ")

            if choice == "0":
                return

            selected = catalogs.get(choice)

            if selected is None:
                self._output("Ошибка: неизвестный пункт меню.")
            else:
                self._run_catalog_entity_menu(*selected)

    def _run_catalog_entity_menu(
        self,
        title: str,
        show: Callable[[], None],
        add: Callable[[], None],
        update: Callable[[], None],
        delete: Callable[[], None],
    ) -> None:
        """Предоставляет операции для выбранного справочника."""
        while True:
            self._output(
                f"\n{title}:\n"
                "1 — Показать список\n"
                "2 — Добавить\n"
                "3 — Изменить\n"
                "4 — Удалить\n"
                "0 — Назад"
            )
            choice = self._input("Выбор: ")

            if choice == "1":
                show()
            elif choice == "2":
                add()
            elif choice == "3":
                update()
            elif choice == "4":
                delete()
            elif choice == "0":
                return
            else:
                self._output("Ошибка: неизвестный пункт меню.")

    def _run_student_menu(self) -> None:
        """Показывает Студенту расписание его группы."""
        group_id = self._read_id("ID вашей учебной группы: ")

        if group_id is not None:
            self._schedule_cli.show_student_schedule(group_id)

    def _run_teacher_menu(self) -> None:
        """Показывает Преподавателю его занятия."""
        teacher_id = self._read_id("ID преподавателя: ")

        if teacher_id is not None:
            self._schedule_cli.show_teacher_schedule(teacher_id)

    def _read_id(self, prompt: str) -> int | None:
        """Считывает целочисленный идентификатор."""
        value = self._input(prompt)

        try:
            return int(value)
        except ValueError:
            self._output("Ошибка: идентификатор должен быть целым числом.")
            return None

    def _read_weekday(self) -> Weekday | None:
        """Считывает день недели по номеру."""
        self._output(
            "1 — Понедельник, 2 — Вторник, 3 — Среда, "
            "4 — Четверг, 5 — Пятница, 6 — Суббота, "
            "7 — Воскресенье."
        )

        value = self._input("Номер дня недели: ")

        try:
            number = int(value)
        except ValueError:
            self._output("Ошибка: номер дня должен быть целым числом.")
            return None

        weekdays = list(Weekday)

        if number < 1 or number > len(weekdays):
            self._output("Ошибка: номер дня недели должен быть от 1 до 7.")
            return None

        return weekdays[number - 1]