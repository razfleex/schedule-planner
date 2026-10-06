import unittest

from schedule_planner.catalog_service import CatalogService
from schedule_planner.models import Classroom, Group, Subject, Teacher


class TestCatalogService(unittest.TestCase):
    """Тесты бизнес-логики каталога справочных сущностей."""

    def setUp(self) -> None:
        """Инициализация чистого сервиса перед каждым тестом."""
        self.service = CatalogService()

    def test_teacher_crud_and_errors(self) -> None:
        """Проверка CRUD операций и обработки ошибок для Преподавателя."""
        teacher = Teacher(id=1, full_name="Иван Иванов")
        self.service.add_teacher(teacher)

        fetched = self.service.get_teacher_by_id(1)
        self.assertEqual(fetched, teacher)
        self.assertEqual(self.service.get_all_teachers(), [teacher])

        updated = Teacher(id=1, full_name="Иван Петров")
        self.service.update_teacher(updated)
        fetched_updated = self.service.get_teacher_by_id(1)
        self.assertIsNotNone(fetched_updated)
        if fetched_updated:
            self.assertEqual(fetched_updated.full_name, "Иван Петров")

        with self.assertRaises(ValueError):
            self.service.add_teacher(Teacher(id=1, full_name="Дубликат"))

        self.service.delete_teacher(1)
        self.assertIsNone(self.service.get_teacher_by_id(1))
        self.assertEqual(self.service.get_all_teachers(), [])

        with self.assertRaises(ValueError):
            self.service.update_teacher(Teacher(id=999, full_name="Несуществующий"))

        with self.assertRaises(ValueError):
            self.service.delete_teacher(999)

    def test_group_crud_and_errors(self) -> None:
        """Проверка CRUD операций и обработки ошибок для Учебной группы."""
        group = Group(id=1, name="ИВТ-201")
        self.service.add_group(group)

        fetched = self.service.get_group_by_id(1)
        self.assertEqual(fetched, group)
        self.assertEqual(self.service.get_all_groups(), [group])

        updated = Group(id=1, name="ИВТ-202")
        self.service.update_group(updated)
        fetched_updated = self.service.get_group_by_id(1)
        self.assertIsNotNone(fetched_updated)
        if fetched_updated:
            self.assertEqual(fetched_updated.name, "ИВТ-202")

        with self.assertRaises(ValueError):
            self.service.add_group(Group(id=1, name="Дубликат"))

        self.service.delete_group(1)
        self.assertIsNone(self.service.get_group_by_id(1))
        self.assertEqual(self.service.get_all_groups(), [])

        with self.assertRaises(ValueError):
            self.service.update_group(Group(id=999, name="Несуществующая"))

        with self.assertRaises(ValueError):
            self.service.delete_group(999)

    def test_subject_crud_and_errors(self) -> None:
        """Проверка CRUD операций и обработки ошибок для Дисциплины."""
        subject = Subject(id=1, name="Программирование")
        self.service.add_subject(subject)

        fetched = self.service.get_subject_by_id(1)
        self.assertEqual(fetched, subject)
        self.assertEqual(self.service.get_all_subjects(), [subject])

        updated = Subject(id=1, name="Математика")
        self.service.update_subject(updated)
        fetched_updated = self.service.get_subject_by_id(1)
        self.assertIsNotNone(fetched_updated)
        if fetched_updated:
            self.assertEqual(fetched_updated.name, "Математика")

        with self.assertRaises(ValueError):
            self.service.add_subject(Subject(id=1, name="Дубликат"))

        self.service.delete_subject(1)
        self.assertIsNone(self.service.get_subject_by_id(1))
        self.assertEqual(self.service.get_all_subjects(), [])

        with self.assertRaises(ValueError):
            self.service.update_subject(Subject(id=999, name="Несуществующая"))

        with self.assertRaises(ValueError):
            self.service.delete_subject(999)

    def test_classroom_crud_and_errors(self) -> None:
        """Проверка CRUD операций и обработки ошибок для Аудитории."""
        classroom = Classroom(id=1, name="101-А")
        self.service.add_classroom(classroom)

        fetched = self.service.get_classroom_by_id(1)
        self.assertEqual(fetched, classroom)
        self.assertEqual(self.service.get_all_classrooms(), [classroom])

        updated = Classroom(id=1, name="102-Б")
        self.service.update_classroom(updated)
        fetched_updated = self.service.get_classroom_by_id(1)
        self.assertIsNotNone(fetched_updated)
        if fetched_updated:
            self.assertEqual(fetched_updated.name, "102-Б")

        with self.assertRaises(ValueError):
            self.service.add_classroom(Classroom(id=1, name="Дубликат"))

        self.service.delete_classroom(1)
        self.assertIsNone(self.service.get_classroom_by_id(1))
        self.assertEqual(self.service.get_all_classrooms(), [])

        with self.assertRaises(ValueError):
            self.service.update_classroom(Classroom(id=999, name="Несуществующая"))

        with self.assertRaises(ValueError):
            self.service.delete_classroom(999)


if __name__ == "__main__":
    unittest.main()