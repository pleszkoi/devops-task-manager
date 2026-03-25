# Ez definiálja az API adatmodelljeit.
# 
# Ezeket a modelleket használja a FastAPI:
#  - request validálásra
#  - response generálásra
#  - OpenAPI dokumentációra (Swagger UI)
#  - típusellenőrzésre

# Enum: egy Python beépített típus, ami fix értékkészletet definiál.

# BaseModel: a Pydantic alap osztálya.
# Ezt csinálja:
#  - JSON → Python objektum
#  - validáció
#  - típusellenőrzés
#  - dokumentáció generálás
# FastAPI szinte minden adatmodellje BaseModel lesz.

# Field: a Pydantic mező konfigurációja.
# Ennek segítségével lehet:
#  - validációt beállítani
#  - default értéket adni
#  - metadata-t megadni

# ConfigDict: a Pydantic v2 config rendszere.

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

# Enum osztály
# class TaskStatus(Enum): -> JSON-ben: TaskStatus.todo -> Nem API barát
# class TaskStatus(str, Enum): -> JSON-ben: "todo" 

class TaskStatus(str, Enum):

    # A status mező csak ezeket az értékeket veheti fel
    # Ha API-ba más jön, pl.: "status": "sleeping" akkor a FastAPI automatikusan hibát dob.

    todo = "todo"
    doing = "doing"
    done = "done"

# Ez a modell a task létrehozására szolgál.
# Amikor POST request jön: POST /api/v1/tasks a body-t ez a modell validálja.

class TaskCreate(BaseModel):

    # Típust is ellenőriz (str) és a title hosszát is ellenőrzi
    # Ha megszegik: FastAPI automatikusan ad: 422 Unprocessable Entity

    title: str = Field(min_length=1, max_length=200)

    # Ez Python 3.10+ union típus.
    # str | None -> azt jelenti, hogy lehet string vagy lehet None

    description: str | None = Field(default=None, max_length=2000)
    
    # Két dolgot csinál:
    #  - típus megkötés -> TaskStatus, tehát csak az enum értékek engedélyezettek.
    #  - default -> Ha nincs a requestben, akkor automatikusan: status = "todo"

    status: TaskStatus = TaskStatus.todo

# Ez a modell a task módosítására szolgál.
# Azért kell külön modell, mert update-nél nem minden mező kötelező.

class TaskUpdate(BaseModel):

    # Ez azt jelenti: lehet None, de ha nem None → validáció érvényes

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    # Ha nincs a body-ban: nem változtatjuk Ha van: frissítjük

    status: TaskStatus | None = None

# Ez a response modell.
# Amikor a FastAPI visszaad adatot: response_model=TaskOut akkor ezt a struktúrát használja.

class TaskOut(BaseModel):
    # Ez a modell viselkedését állítja.
    # from_attributes=True:
    # Engedélyezi, hogy TaskOut.model_validate(task) működjön akkor is, ha task nem dict, hanem objektum.
    # Lehetővé teszi, hogy a Pydantic modellek közvetlenül SQLAlchemy objektumokból épüljenek fel manuális mezőmásolás nélkül.
    # A task_repo_db.py-ban működni fog a return TaskOut.model_validate(task)
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus