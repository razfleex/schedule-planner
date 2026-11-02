from schedule_planner.database.lesson_model import LessonORM
from schedule_planner.models import (
    Classroom,
    Group,
    Lesson,
    Subject,
    Teacher,
)


class LessonMapper:
    """Преобразует занятия между доменной и ORM-моделью."""

    @staticmethod
    def to_orm(lesson: Lesson) -> LessonORM:
        """Преобразует объект Lesson в модель SQLAlchemy."""
        return LessonORM(
            id=lesson.id,
            teacher_id=lesson.teacher.id,
            group_id=lesson.group.id,
            subject_id=lesson.subject.id,
            classroom_id=lesson.classroom.id,
            day_of_week=lesson.day_of_week,
            start_time=lesson.start_time,
            end_time=lesson.end_time,
        )

    @staticmethod
    def to_domain(orm_lesson: LessonORM) -> Lesson:
        """Создаёт Lesson из ORM-модели с загруженными связями."""
        return Lesson(
            id=orm_lesson.id,
            teacher=Teacher(
                id=orm_lesson.teacher.id,
                full_name=orm_lesson.teacher.full_name,
            ),
            group=Group(
                id=orm_lesson.group.id,
                name=orm_lesson.group.name,
            ),
            subject=Subject(
                id=orm_lesson.subject.id,
                name=orm_lesson.subject.name,
            ),
            classroom=Classroom(
                id=orm_lesson.classroom.id,
                name=orm_lesson.classroom.name,
            ),
            day_of_week=orm_lesson.day_of_week,
            start_time=orm_lesson.start_time,
            end_time=orm_lesson.end_time,
        )
