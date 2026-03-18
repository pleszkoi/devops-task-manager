from sqlalchemy.orm import Session
from devops_task_manager.models.task import TaskCreate, TaskUpdate, TaskOut
from devops_task_manager.models.task_db import TaskDB


class TaskRepoDB:

    # egy SQLAlchemy Session-t kap és
    # eltárolja magában

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[TaskOut]:

        # Ez SQL-re fordul:
        # SELECT * FROM tasks;

        tasks = self.db.query(TaskDB).all()
        return [
            TaskOut(
                id=t.id,
                title=t.title,
                description=t.description,
                status=t.status,
            )
            for t in tasks
        ]

    def get(self, task_id: int) -> TaskOut | None:

        # SELECT * FROM tasks WHERE id = ? LIMIT 1;

        task = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task:
            return None

        return TaskOut(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
        )

    def create(self, data: TaskCreate) -> TaskOut:
        
        # ORM objektum létrehozása. Ez még csak Python objektum.

        task = TaskDB(
            title=data.title,
            description=data.description,
            # Azért .value, mert TaskStatus.todo nem string, hanem enum. De a DB-ben string kell: "todo"
            status=data.status.value,
        )
        # Session-be rakás. Ez még nem SQL.

        self.db.add(task)
        
        # Itt történik: INSERT INTO tasks ...
        
        self.db.commit()

        # Az id csak DB-ben generálódik. commit után visszatölti az objektumba

        self.db.refresh(task)

        return TaskOut(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
        )

    def update(self, task_id: int, data: TaskUpdate) -> TaskOut | None:
        task = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task:
            return None

        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status.value

        # UPDATE tasks SET ... WHERE id=...
        
        self.db.commit()

        # Friss adat visszatöltése.
        
        self.db.refresh(task)

        return TaskOut(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
        )

    def delete(self, task_id: int) -> bool:
        task = self.db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if not task:
            return False

        self.db.delete(task)

        # DELETE FROM tasks WHERE id=...

        self.db.commit()
        
        return True

# A task_repo_db.py:
#  - SQLAlchemy sessionnel dolgozik
#  - DB modelt használ (TaskDB)
#  - API modelt ad vissza (TaskOut)
#  - CRUD műveleteket valósít meg
#  - izolálja az adatbázis logikát
