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

from fastapi import APIRouter, HTTPException
from devops_task_manager.models.task import TaskCreate, TaskUpdate, TaskOut
from devops_task_manager.services.task_service import TaskService

# Router létrehozása
# prefix="/api/v1/tasks" -> Ez azt jelenti, hogy az összes alatta lévő endpoint automatikusan ezzel a prefixszel indul.
# tags=["tasks"] -> Ez főleg a Swagger UI-ban fontos. A /docs oldalon a route-ok csoportosítva jelennek meg tasks név alatt.

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# Ez egy segédfüggvény. Visszaadja a globális task_service példányt a main.py-ból.

def get_service() -> TaskService:

    # Egyszerű dependency megoldás Week1-re.
    # Week2-ben DI + DB repo jön.
    # A main.py-ban van: task_service = TaskService(TaskRepoMemory())
    # Tehát ez az egyetlen service példány él az appban.

    from devops_task_manager.main import task_service
    return task_service

# A task lista endpoint.
# @router.get("") jelentése: 
#  - HTTP method: GET
#  - útvonal: ""
#  - a prefix miatt a teljes endpoint: /api/v1/tasks
# 
# response_model=list[TaskOut]
# Ez azt mondja a FastAPI-nak, hogy a válasz egy TaskOut objektumokból álló lista lesz.

@router.get("", response_model=list[TaskOut])
def list_tasks():

    # A service-ből elkéri az összes taskot, és visszaadja. A service végül a repository list() metódusához jut.

    return get_service().list_tasks()

# A task létrehozó endpoint.
# A 201 jelentése: resource created. Ez REST API szempontból helyesebb, mint a 200.

@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate):
    return get_service().create_task(data)

# Egy konkrét task lekérdezése.

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    task = get_service().get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# A task frissítése.

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate):
    task = get_service().update_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# A task törlése.
# A 204 jelentése: No Content. Ez nagyon tipikus DELETE válasz.
# Azt jelenti: sikeres volt, nincs response body

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    ok = get_service().delete_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

# A route réteg feladatai:
#  - HTTP method hozzárendelés
#  - URL-ek kezelése
#  - request body validáció
#  - response model definiálása
#  - HTTP hibák kezelése
#  - státuszkódok meghatározása
#
# A service réteg feladata:
#  - üzleti logika
#
# A repository feladata:
#  - adatkezelés
#
# Ez a szétválasztás nagyon fontos.