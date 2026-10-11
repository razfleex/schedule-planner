from collections.abc import Callable

from schedule_planner.catalog_service import CatalogService
from schedule_planner.models import Classroom, Group, Subject, Teacher


class CatalogCli:
    """Предоставляет терминальное управление справочниками системы."""

    def __init__(
        self,
        catalog_service: CatalogService,
        input_func: Callable[[str], str] = input,
        output: Callable[[str], None] = print,
    ) -> None:
        """Инициализирует CLI с сервисом справочников и функциями ввода-вывода."""
        self._service = catalog_service
        self._input = input_func
        self._output = output

    def show_teachers(self) -> None:
        """Показывает всех преподавателей."""
        teachers = self._service.get_all_teachers()
        if not teachers:
            self._output("Список пуст.")
            return
        for teacher in teachers:
            self._output(f"[{teacher.id}] {teacher.full_name}")

    def add_teacher(self) -> None:
        """Добавляет нового преподавателя."""
        try:
            teacher_id = self._read_id()
            full_name = self._input("Введите ФИО: ")
            teacher = Teacher(id=teacher_id, full_name=full_name)
            self._service.add_teacher(teacher)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Преподаватель {teacher_id} добавлен.")

    def update_teacher(self) -> None:
        """Изменяет существующего преподавателя."""
        try:
            teacher_id = self._read_id()
            full_name = self._input("Введите новое ФИО: ")
            teacher = Teacher(id=teacher_id, full_name=full_name)
            self._service.update_teacher(teacher)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Преподаватель {teacher_id} изменён.")

    def delete_teacher(self) -> None:
        """Удаляет преподавателя по ID."""
        try:
            teacher_id = self._read_id()
            self._service.delete_teacher(teacher_id)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Преподаватель {teacher_id} удалён.")

    def show_groups(self) -> None:
        """Показывает все учебные группы."""
        groups = self._service.get_all_groups()
        if not groups:
            self._output("Список пуст.")
            return
        for group in groups:
            self._output(f"[{group.id}] {group.name}")

    def add_group(self) -> None:
        """Добавляет новую учебную группу."""
        try:
            group_id = self._read_id()
            name = self._input("Введите название группы: ")
            group = Group(id=group_id, name=name)
            self._service.add_group(group)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Учебная группа {group_id} добавлена.")

    def update_group(self) -> None:
        """Изменяет существующую учебную группу."""
        try:
            group_id = self._read_id()
            name = self._input("Введите новое название группы: ")
            group = Group(id=group_id, name=name)
            self._service.update_group(group)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Учебная группа {group_id} изменена.")

    def delete_group(self) -> None:
        """Удаляет учебную группу по ID."""
        try:
            group_id = self._read_id()
            self._service.delete_group(group_id)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Учебная группа {group_id} удалена.")

    def show_subjects(self) -> None:
        """Показывает все дисциплины."""
        subjects = self._service.get_all_subjects()
        if not subjects:
            self._output("Список пуст.")
            return
        for subject in subjects:
            self._output(f"[{subject.id}] {subject.name}")

    def add_subject(self) -> None:
        """Добавляет новую дисциплину."""
        try:
            subject_id = self._read_id()
            name = self._input("Введите название дисциплины: ")
            subject = Subject(id=subject_id, name=name)
            self._service.add_subject(subject)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Дисциплина {subject_id} добавлена.")

    def update_subject(self) -> None:
        """Изменяет существующую дисциплину."""
        try:
            subject_id = self._read_id()
            name = self._input("Введите новое название дисциплины: ")
            subject = Subject(id=subject_id, name=name)
            self._service.update_subject(subject)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Дисциплина {subject_id} изменена.")

    def delete_subject(self) -> None:
        """Удаляет дисциплину по ID."""
        try:
            subject_id = self._read_id()
            self._service.delete_subject(subject_id)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Дисциплина {subject_id} удалена.")

    def show_classrooms(self) -> None:
        """Показывает все аудитории."""
        classrooms = self._service.get_all_classrooms()
        if not classrooms:
            self._output("Список пуст.")
            return
        for classroom in classrooms:
            self._output(f"[{classroom.id}] {classroom.name}")

    def add_classroom(self) -> None:
        """Добавляет новую аудиторию."""
        try:
            classroom_id = self._read_id()
            name = self._input("Введите название аудитории: ")
            classroom = Classroom(id=classroom_id, name=name)
            self._service.add_classroom(classroom)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Аудитория {classroom_id} добавлена.")

    def update_classroom(self) -> None:
        """Изменяет существующую аудиторию."""
        try:
            classroom_id = self._read_id()
            name = self._input("Введите новое название аудитории: ")
            classroom = Classroom(id=classroom_id, name=name)
            self._service.update_classroom(classroom)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Аудитория {classroom_id} изменена.")

    def delete_classroom(self) -> None:
        """Удаляет аудиторию по ID."""
        try:
            classroom_id = self._read_id()
            self._service.delete_classroom(classroom_id)
        except ValueError as error:
            self._output(f"Ошибка: {error}")
            return
        self._output(f"Аудитория {classroom_id} удалена.")

    def _read_id(self) -> int:
        """Считывает целочисленный ID или сообщает о неверном формате."""
        value = self._input("Введите ID: ")
        try:
            return int(value)
        except ValueError as error:
            raise ValueError("ID должен быть целым числом.") from error
