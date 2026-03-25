# A service réteg most még egyszerűnek tűnik, de nagyon fontos, mert később ide kerülhet:
#  - üzleti logika
#  - plusz validáció
#  - logging
#  - audit
#  - metrikák
#  - több repository összehangolása
#  - tranzakciók

from devops_task_manager.models.task import TaskCreate, TaskUpdate, TaskOut
from devops_task_manager.repositories.interfaces import TaskRepository

# A service réteg.
# A szerepe:
#  - ne a route-ok beszéljenek közvetlenül a repositoryval
#  - legyen egy köztes réteg, ahol üzleti logikát lehet elhelyezni

class TaskService:

    # Ez azt jelenti, hogy bármilyen objektum jöhet, ami megfelel a TaskRepository szerződésnek
    
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    # A service lista metódusa. Egyszerűen továbbhívja a repository list() metódusát.
    # Azért nem hívja a route közvetlenül a repositoryt, mert:
    #  - a route réteg össze lenne keverve az adatkezeléssel
    #  - később nehezebb lenne plusz logikát betenni

    def list_tasks(self) -> list[TaskOut]:
        return self.repo.list()

    # Lekér egy taskot ID alapján.
    # Azért nem dob itt rögtön hibát, mert a service itt még nem HTTP szinten gondolkodik.
    # A service üzleti logika réteg, nem web réteg.
    # A 404-es HTTP hibát a route dobja, mert az már a HTTP világ része.
    # Ez fontos szétválasztás:
    #  - service → Python értékekkel dolgozik
    #  - route → HTTP státuszkódokat kezel

    def get_task(self, task_id: int) -> TaskOut | None:
        return self.repo.get(task_id)
    
    # Új taskot hoz létre.
    # Ez már validált adat, mert a FastAPI előtte ellenőrizte.
    # A service itt később tud majd:
    #  - title duplikáció ellenőrzés
    #  - üzleti szabályok
    #  - log írás
    #  - event küldés

    def create_task(self, data: TaskCreate) -> TaskOut:
        return self.repo.create(data)

    # Frissíti a taskot.

    def update_task(self, task_id: int, data: TaskUpdate) -> TaskOut | None:
        return self.repo.update(task_id, data)

    # Töröl egy taskot.

    def delete_task(self, task_id: int) -> bool:
        return self.repo.delete(task_id)

# Route vs Service vs Repository
#
# Route
# A HTTP világgal foglalkozik:
#  - URL
#  - method
#  - request/response
#  - státuszkód
#  - HTTP hiba
#
# Service
# Az üzleti logikával foglalkozik:
#  - szabályok
#  - döntések
#  - munkafolyamat
#  - több adatforrás összehangolása
#
# Repository
# Az adattal foglalkozik:
#  - tárolás
#  - lekérés
#  - update
#  - delete