from typing import Protocol


class HasId(Protocol):
    """Протокол для сущностей, имеющих целочисленный идентификатор."""

    id: int


class InMemoryRepository[T: HasId]:
    """Универсальное In-Memory хранилище сущностей."""

    def __init__(self) -> None:
        """Инициализирует пустое хранилище."""
        self._storage: dict[int, T] = {}

    def add(self, entity: T) -> T:
        """Добавляет сущность в хранилище.

        Raises:
            ValueError: Если сущность с таким id уже существует.
        """
        if entity.id in self._storage:
            raise ValueError(f"Сущность с id={entity.id} уже существует.")
        self._storage[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: int) -> T | None:
        """Возвращает сущность по id или None, если она не найдена."""
        return self._storage.get(entity_id)

    def get_all(self) -> list[T]:
        """Возвращает список всех сохранённых сущностей."""
        return list(self._storage.values())

    def update(self, entity: T) -> T:
        """Обновляет существующую сущность.

        Raises:
            ValueError: Если сущность с таким id не найдена.
        """
        if entity.id not in self._storage:
            raise ValueError(f"Сущность с id={entity.id} не найдена для обновления.")
        self._storage[entity.id] = entity
        return entity

    def delete(self, entity_id: int) -> None:
        """Удаляет сущность по id.

        Raises:
            ValueError: Если сущность с таким id не найдена.
        """
        if entity_id not in self._storage:
            raise ValueError(f"Сущность с id={entity_id} не найдена для удаления.")
        del self._storage[entity_id]