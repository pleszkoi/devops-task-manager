# Ez importálja a FastAPI framework fő osztályát.
# A FastAPI objektum reprezentálja az egész webalkalmazást.
# Minden route, middleware, config ehhez az objektumhoz tartozik.

# a Python beépített modulja, amivel többek között környezeti változókat lehet olvasni.
import os

# Az asynccontextmanager egy dekorátor, amivel olyan függvényt írhatsz, ami:
#  - belépési logikát futtat,
#  - aztán átadja a vezérlést,
#  - majd kilépési logikát futtat.
from contextlib import asynccontextmanager

from fastapi import FastAPI
from devops_task_manager.core.config import settings
from devops_task_manager.core.database import Base, engine

# A router as ... azt jelenti: router → health_router
# Átnevezzük, mert minden route fájlban az objektum neve router, és így elkerüljük az ütközést.

from devops_task_manager.api.routes.health import router as health_router
from devops_task_manager.api.routes.tasks import router as tasks_router
from devops_task_manager.api.routes.debug import router as debug_router

# dekorátor
# Azt mondja, hogy az alatta lévő függvény ne egyszerű async függvényként működjön, hanem egy aszinkron context managerként.
# Ez kell ahhoz, hogy a FastAPI lifespan= paraméterrel használni tudja.
# Ez teszi alkalmassá a lifespan() függvényt arra, hogy a FastAPI indulás/leállás kezelésére használja.
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Megnézi, hogy létezik-e INIT_DB nevű env var.
    # ha nincs beállítva, akkor "true" lesz az eredmény,
    # ha INIT_DB=false, akkor "false" lesz az eredmény.

    if os.getenv("INIT_DB", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)
    # a yield előtti rész az induláskor fut le,
    # a yield után “átadod” az alkalmazást normál futásra,
    # a yield utáni rész leálláskor futna le.
    # Ebben az esetben nincs shutdown logika, ezért a yield után nincs semmi.
    yield

# FastAPI alkalmazás létrehozása
# Memóriában:
#
# app
# │
# ├─ routes
# ├─ middleware
# ├─ dependency graph
# └─ openapi schema
#
# A paraméterek a Swagger UI-ban jelennek meg.

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    # Ezzel lehet megmondani a FastAPI-nak, hogy az alkalmazás életciklusát a lifespan() függvény kezelje
    lifespan=lifespan,
)

# Root endpoint
#
# Egy route dekorátor.
# Ez azt jelenti: GET / -> hívásnál ez a függvény fut.
# A dekorátor regisztrálja a route-ot az appban.

@app.get("/")
def root():

    # Ez egy dictionary. A FastAPI ezt automatikusan JSON-ná alakítja.
    # Ez egy nagyon gyakori microservice endpoint.
    # Használható például:
    #  - health check
    #  - debug
    #  - verzió ellenőrzés
    #  - deployment ellenőrzés

    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "version": settings.app_version,
    }

# Routerek regisztrálása

# hozzáadja a health endpointokat.
# Például:
#  - /health
#  - /ready

app.include_router(health_router)

# hozzáadja a task endpointokat.
#  - GET /api/v1/tasks
#  - POST /api/v1/tasks
#  - PUT /api/v1/tasks/{id}
#  - DELETE /api/v1/tasks/{id}

app.include_router(tasks_router)

# a debug endpoint.
#  - /api/v1/debug/podinfo

app.include_router(debug_router)


# A háttérben a FastAPI összeépíti az útvonalakat.
#
# Memória modell:
#
# app
# │
# ├─ "/"
# ├─ "/health"
# ├─ "/ready"
# ├─ "/api/v1/tasks"
# ├─ "/api/v1/tasks/{id}"
# └─ "/api/v1/debug/podinfo"

# A main.py:
#  - létrehozza a FastAPI alkalmazást
#  - példányosítja a service-t és repositoryt
#  - regisztrálja a routereket
#  - definiál egy alap endpointot
# Ez az alkalmazás belépési pontja.