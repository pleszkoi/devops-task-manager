# APIRouter
# A FastAPI-ban a route-okat lehet közvetlenül az app objektumra rakni, de jobb külön routerekbe szervezni őket.
# A tasks.py egy külön router:
#  - csak task endpointok
#  - átláthatóbb
#  - később lehet külön health.py, debug.py, auth.py
#
# HTTPException
# Ezzel tudsz szabályos HTTP hibát visszaadni.

# Modellek
# TaskCreate: POST body
# TaskUpdate: PUT body
# TaskOut: response body
#
# TaskService
# A route nem közvetlenül a repositoryt hívja, hanem a service réteget. Ez tisztább architektúra.

# A get_db() típusjelöléséhez kell.
# A get_db() nem simán return-nel ad vissza értéket, hanem yield-et használ, ezért generator jellegű dependency.

from collections.abc import Generator

# Depends: a dependency injectionhöz kell.

from fastapi import APIRouter, Depends, HTTPException

# a konkrét SQLAlchemy session típus. Ezzel tudjuk szépen típusozni a get_db() és get_service() függvényeket.

from sqlalchemy.orm import Session

from devops_task_manager.models.task import TaskCreate, TaskUpdate, TaskOut
from devops_task_manager.services.task_service import TaskService

# TaskRepoDB:
# A PostgreSQL-es repository.
# 
# SessionLocal
# A database.py-ból jön.

from devops_task_manager.repositories.task_repo_db import TaskRepoDB
from devops_task_manager.core.database import SessionLocal

# Router létrehozása
# prefix="/api/v1/tasks" -> Ez azt jelenti, hogy az összes alatta lévő endpoint automatikusan ezzel a prefixszel indul.
# tags=["tasks"] -> Ez főleg a Swagger UI-ban fontos. A /docs oldalon a route-ok csoportosítva jelennek meg tasks név alatt.

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def get_db() -> Generator[Session, None, None]:
    # Létrehoz egy új DB sessiont.
    db = SessionLocal()
    try:
        # Átadja ezt a sessiont annak, aki kéri.
        yield db
    finally:
        # A request végén biztosan bezárja.
        db.close()

# A FastAPI:
# 1. meghívja a get_db()-t,
# 2. megkapja a sessiont,
# 3. beteszi a db paraméterbe,
# 4. létrehozza a TaskRepoDB(db)-t,
# 5. létrehozza a TaskService(...)-t,
# 6. és ezt adja tovább az endpointnak.

def get_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepoDB(db))

# A task lista endpoint.
# @router.get("") jelentése: 
#  - HTTP method: GET
#  - útvonal: ""
#  - a prefix miatt a teljes endpoint: /api/v1/tasks
# 
# response_model=list[TaskOut]
# Ez azt mondja a FastAPI-nak, hogy a válasz egy TaskOut objektumokból álló lista lesz.

@router.get("", response_model=list[TaskOut])

# service: TaskService = Depends(get_service)
#  - a route meghívása előtt a FastAPI meghívja a get_service() függvényt,
#  - annak eredményét beteszi a service paraméterbe.
# És ha a get_service() maga is függ valamitől, például a DB sessiontől, akkor azt is a FastAPI oldja meg.
# Ez egy dependency lánc.

def list_tasks(service: TaskService = Depends(get_service)):
    return service.list_tasks()


@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, service: TaskService = Depends(get_service)):
    return service.create_task(data)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, service: TaskService = Depends(get_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: TaskService = Depends(get_service),
):
    task = service.update_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, service: TaskService = Depends(get_service)):
    ok = service.delete_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
