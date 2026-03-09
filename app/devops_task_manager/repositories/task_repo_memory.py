# A jelenlegi app adat-tároló rétege: most memóriában tárol, később ugyanennek a szerepét veszi át a DB-s repository.

# Dict: Típusannotációhoz kell. Python 3.9+ óta lehetne dict[int, TaskOut] is, de a Dict még gyakori.
# Modellek importja:
#  - TaskCreate: amit a POST request body-ból kapsz
#  - TaskUpdate: amit update-hez kapsz
#  - TaskOut: amit visszaadsz (id-val együtt)

from typing import Dict
from devops_task_manager.models.task import TaskCreate, TaskUpdate, TaskOut

# Ez az “in-memory adatbázis”. Egy példányában él a teljes tárolt állapot.

#Fontos következmény (DevOps szemmel):
#  - Ha a folyamat újraindul (uvicorn restart, pod restart) → minden adat elveszik.
#  - Ha több pod fut → mindegyik podnak külön memóriája van → adatok szétcsúsznak.
#    Ezért kell majd Week 2-ben PostgreSQL.

class TaskRepoMemory:
    
    # Kunstruktor:
    # _tasks: Ez egy dict:
    #  - kulcs: int (task id)
    #  - érték: TaskOut (a task objektum)

    def __init__(self) -> None:
        self._tasks: Dict[int, TaskOut] = {}
        self._next_id: int = 1

    # A dict.values() egy “nézet”, nem lista. A list(...) tényleges listát csinál belőle.
    # Az összes taskot adja vissza, egy listában.

    def list(self) -> list[TaskOut]:
        return list(self._tasks.values())

    # A dict.get(key): ha van ilyen kulcs → értéket ad, ha nincs → None
    # Ez kényelmesebb, mint try/except.

    def get(self, task_id: int) -> TaskOut | None:
        return self._tasks.get(task_id)

    # 3 lépsből áll:
    # 1. TaskOut létrehozása:
    #  - A kliens TaskCreate-ot küld (abban nincs id).
    #  - A repo létrehozza a “kész” taskot (TaskOut) az ID-val.

    # 2. Tárolás dict-ben: A kulcs az id, érték a task objektum.

    # 3. ID növelés: Hogy a következő create új id-t kapjon.

    def create(self, data: TaskCreate) -> TaskOut:
        task = TaskOut(
            id=self._next_id,
            title=data.title,
            description=data.description,
            status=data.status,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    # Meglévő task keresése: 
    # Ha nincs ilyen id, akkor update nem lehetséges, ezért None-t ad vissza.
    # A service/router majd ezt 404-re fordítja.

    def update(self, task_id: int, data: TaskUpdate) -> TaskOut | None:
        existing = self._tasks.get(task_id)
        if not existing:
            return None

        # data.model_dump(): A Pydantic modelből csinál egy dictet.
        # {k: v for ... if v is not None} kiszűri a None értékeket. Tehát csak azt frissítjük, amit a user tényleg megadott.
        # existing.model_copy(update=...): 
        # A TaskOut egy Pydantic model. A model_copy(update=...):
        #  - készít egy másolatot az existing taskról
        #  - rámerge-eli az update dictet
        #  - így kapunk egy új, módosított TaskOut-ot

        updated = existing.model_copy(update={
            k: v for k, v in data.model_dump().items() if v is not None
        })

        # Beírja az updated taskot

        self._tasks[task_id] = updated
        return updated

    # A dict.pop(key, default):
    #  - kiveszi a kulcsot
    #  - visszaadja az értéket, ha volt
    #  - ha nem volt, akkor a defaultot adja (itt None)

    # A kód ezt bool-lá alakítja:
    #  - ha volt task → visszatér egy TaskOut-tal → is not None → True
    #  - ha nem volt → None → False

    # Ezt a router 204 vs 404 logikában használja.

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None