from schedule_planner.catalog_repository import InMemoryRepository
from schedule_planner.catalog_usage_checker import CatalogUsageChecker
from schedule_planner.models import Classroom, Group, Subject, Teacher


class CatalogService:
    """Сервис бизнес-логики для управления справочными сущностями системы."""

    def __init__(
        self,
        teacher_repo: InMemoryRepository[Teacher] | None = None,
        group_repo: InMemoryRepository[Group] | None = None,
        subject_repo: InMemoryRepository[Subject] | None = None,
        classroom_repo: InMemoryRepository[Classroom] | None = None,
        usage_checker: CatalogUsageChecker | None = None,
    ) -> None:
        """Инициализирует сервис с репозиториями и проверкой использования."""
        self._teacher_repo = (
            teacher_repo
            if teacher_repo is not None
            else InMemoryRepository[Teacher]()
        )
        self._group_repo = (
            group_repo
            if group_repo is not None
            else InMemoryRepository[Group]()
        )
        self._subject_repo = (
            subject_repo
            if subject_repo is not None
            else InMemoryRepository[Subject]()
        )
        self._classroom_repo = (
            classroom_repo
            if classroom_repo is not None
            else InMemoryRepository[Classroom]()
        )
        self._usage_checker = usage_checker

    def add_teacher(self, teacher: Teacher) -> Teacher:
        """Добавляет преподавателя в каталог."""
        return self._teacher_repo.add(teacher)

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        """Возвращает преподавателя по id."""
        return self._teacher_repo.get_by_id(teacher_id)

    def get_all_teachers(self) -> list[Teacher]:
        """Возвращает список всех преподавателей."""
        return self._teacher_repo.get_all()

    def update_teacher(self, teacher: Teacher) -> Teacher:
        """Обновляет данные преподавателя."""
        return self._teacher_repo.update(teacher)

    def delete_teacher(self, teacher_id: int) -> None:
        """Удаляет преподавателя, если он не используется в занятиях."""
        if self._usage_checker is not None:
            self._usage_checker.ensure_teacher_not_used(teacher_id)

        self._teacher_repo.delete(teacher_id)

    def add_group(self, group: Group) -> Group:
        """Добавляет учебную группу в каталог."""
        return self._group_repo.add(group)

    def get_group_by_id(self, group_id: int) -> Group | None:
        """Возвращает учебную группу по id."""
        return self._group_repo.get_by_id(group_id)

    def get_all_groups(self) -> list[Group]:
        """Возвращает список всех учебных групп."""
        return self._group_repo.get_all()

    def update_group(self, group: Group) -> Group:
        """Обновляет данные учебной группы."""
        return self._group_repo.update(group)

    def delete_group(self, group_id: int) -> None:
        """Удаляет учебную группу, если она не используется в занятиях."""
        if self._usage_checker is not None:
            self._usage_checker.ensure_group_not_used(group_id)

        self._group_repo.delete(group_id)

    def add_subject(self, subject: Subject) -> Subject:
        """Добавляет дисциплину в каталог."""
        return self._subject_repo.add(subject)

    def get_subject_by_id(self, subject_id: int) -> Subject | None:
        """Возвращает дисциплину по id."""
        return self._subject_repo.get_by_id(subject_id)

    def get_all_subjects(self) -> list[Subject]:
        """Возвращает список всех дисциплин."""
        return self._subject_repo.get_all()

    def update_subject(self, subject: Subject) -> Subject:
        """Обновляет данные дисциплины."""
        return self._subject_repo.update(subject)

    def delete_subject(self, subject_id: int) -> None:
        """Удаляет дисциплину, если она не используется в занятиях."""
        if self._usage_checker is not None:
            self._usage_checker.ensure_subject_not_used(subject_id)

        self._subject_repo.delete(subject_id)

    def add_classroom(self, classroom: Classroom) -> Classroom:
        """Добавляет аудиторию в каталог."""
        return self._classroom_repo.add(classroom)

    def get_classroom_by_id(self, classroom_id: int) -> Classroom | None:
        """Возвращает аудиторию по id."""
        return self._classroom_repo.get_by_id(classroom_id)

    def get_all_classrooms(self) -> list[Classroom]:
        """Возвращает список всех аудиторий."""
        return self._classroom_repo.get_all()

    def update_classroom(self, classroom: Classroom) -> Classroom:
        """Обновляет данные аудитории."""
        return self._classroom_repo.update(classroom)

    def delete_classroom(self, classroom_id: int) -> None:
        """Удаляет аудиторию, если она не используется в занятиях."""
        if self._usage_checker is not None:
            self._usage_checker.ensure_classroom_not_used(classroom_id)

        self._classroom_repo.delete(classroom_id)