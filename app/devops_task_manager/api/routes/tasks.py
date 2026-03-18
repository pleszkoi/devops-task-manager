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

def get_service() -> TaskService:

    # Ez egy session gyár: így lesz belőle konkrét DB session.

    db = SessionLocal()
    repo = TaskRepoDB(db)
    return TaskService(repo)

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

    # Itt nyílik egy új DB session.
    
    db = SessionLocal()

    # Ez azért kell, hogy a session biztosan lezáruljon, akkor is, ha közben hiba történik.
    try:
        # Itt rögtön felépítjük a láncot:
        # Session
        # ↓
        # TaskRepoDB
        # ↓
        # TaskService

        service = TaskService(TaskRepoDB(db))
        return service.list_tasks()
    
    # Ez garantálja, hogy a session bezárul.
    finally:
        db.close()

# A task létrehozó endpoint.
# A 201 jelentése: resource created. Ez REST API szempontból helyesebb, mint a 200.

@router.post("", response_model=TaskOut, status_code=201)

# data: TaskCreate -> A request body automatikusan TaskCreate modellé alakul.

def create_task(data: TaskCreate):
    db = SessionLocal()
    try:
        service = TaskService(TaskRepoDB(db))
        return service.create_task(data)
    finally:
        db.close()

# Egy konkrét task lekérdezése.

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    db = SessionLocal()
    try:
        service = TaskService(TaskRepoDB(db))
        task = service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    finally:
        db.close()

# A task frissítése.

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate):
    db = SessionLocal()
    try:
        service = TaskService(TaskRepoDB(db))
        task = service.update_task(task_id, data)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    finally:
        db.close()

# A task törlése.
# A 204 jelentése: No Content. Ez nagyon tipikus DELETE válasz.
# Azt jelenti: sikeres volt, nincs response body

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    db = SessionLocal()
    try:
        service = TaskService(TaskRepoDB(db))
        ok = service.delete_task(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Task not found")
        return None
    finally:
        db.close()

# A tasks.py most:
#  - HTTP route-okat definiál
#  - request body-t validál
#  - response modelt definiál
#  - hibákat HTTP státuszkódra fordít
#  - requestenként DB sessiont nyit
#  - a service rétegen keresztül a repositoryt hívja
#  - a végén lezárja a sessiont


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
