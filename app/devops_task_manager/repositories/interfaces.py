# Importálja a Protocol típust. Erre azért van szükség, mert ebből készítjük el a repository-szerződést.

from typing import Protocol

# Ezek kellenek a metódusok aláírásához.
# Ez fontos, mert nem csak azt mondjuk meg, hogy “legyen create() metódus”, hanem azt is, hogy:
#  - mit vár bemenetként,
#  - mit ad vissza.

from devops_task_manager.models.task import TaskCreate, TaskUpdate, TaskOut

# Azt jelenti: definiálok egy olyan típust, aminek nem az öröklés a lényege, hanem az, hogy milyen metódusokat várunk el tőle

class TaskRepository(Protocol):
    def list(self) -> list[TaskOut]: ...
    def get(self, task_id: int) -> TaskOut | None: ...
    def create(self, data: TaskCreate) -> TaskOut: ...
    def update(self, task_id: int, data: TaskUpdate) -> TaskOut | None: ...
    def delete(self, task_id: int) -> bool: ...
