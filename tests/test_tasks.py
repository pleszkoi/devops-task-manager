from fastapi.testclient import TestClient

# Ez lesz felülírva teszt közben
from devops_task_manager.api.routes.tasks import get_service

# Ez a FastAPI app
from devops_task_manager.main import app

# Ezekből építjük fel a teszt service-t.
from devops_task_manager.repositories.task_repo_memory import TaskRepoMemory
from devops_task_manager.services.task_service import TaskService


def test_list_tasks_empty() -> None:
    memory_repo = TaskRepoMemory()

    def override_get_service() -> TaskService:
        return TaskService(memory_repo)

    app.dependency_overrides[get_service] = override_get_service

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/tasks")

        # Ez ellenőrzi:
        #  - a route működik,
        #  - a dependency override működik,
        #  - a listázás üres állapotban jó.

        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.clear()


def test_create_and_list_tasks() -> None:
    memory_repo = TaskRepoMemory()

    def override_get_service() -> TaskService:
        return TaskService(memory_repo)

    app.dependency_overrides[get_service] = override_get_service

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/tasks",
                json={
                    "title": "Teszt task",
                    "description": "Első teszt task",
                    "status": "todo",
                },
            )

            # Ez ellenőrzi:
            #  - a request body valid,
            #  - a route jól működik,
            #  - a 201 státuszkód jó,
            #  - a response modell rendben van.

            assert create_response.status_code == 201
            created_task = create_response.json()
            assert created_task["id"] == 1
            assert created_task["title"] == "Teszt task"
            assert created_task["description"] == "Első teszt task"
            assert created_task["status"] == "todo"

            # mivel ugyanaz a memory_repo él tovább, a létrehozott task benne marad.

            list_response = client.get("/api/v1/tasks")

        assert list_response.status_code == 200
        tasks = list_response.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == 1
        assert tasks[0]["title"] == "Teszt task"
    finally:
        app.dependency_overrides.clear()


def test_get_missing_task_returns_404() -> None:
    memory_repo = TaskRepoMemory()

    def override_get_service() -> TaskService:
        return TaskService(memory_repo)

    app.dependency_overrides[get_service] = override_get_service

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/tasks/999")

        # Ez azt ellenőrzi, hogy:
        #  - a service None-t ad vissza,
        #  - a route ezt helyesen 404-re fordítja.

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}
    finally:
        app.dependency_overrides.clear()


def test_update_task() -> None:
    memory_repo = TaskRepoMemory()

    def override_get_service() -> TaskService:
        return TaskService(memory_repo)

    app.dependency_overrides[get_service] = override_get_service

    # Ez teszteli:
    #  - create működik
    #  - update működik
    #  - a route helyesen adja vissza a frissített objektumot

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/tasks",
                json={
                    "title": "Régi cím",
                    "description": "Régi leírás",
                    "status": "todo",
                },
            )

            assert create_response.status_code == 201
            created_task = create_response.json()
            task_id = created_task["id"]

            update_response = client.put(
                f"/api/v1/tasks/{task_id}",
                json={
                    "title": "Új cím",
                    "description": "Új leírás",
                    "status": "doing",
                },
            )

        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["id"] == task_id
        assert updated_task["title"] == "Új cím"
        assert updated_task["description"] == "Új leírás"
        assert updated_task["status"] == "doing"
    finally:
        app.dependency_overrides.clear()


def test_delete_task() -> None:
    memory_repo = TaskRepoMemory()

    def override_get_service() -> TaskService:
        return TaskService(memory_repo)

    app.dependency_overrides[get_service] = override_get_service

    # Ez teszteli:
    #  - delete működik
    #  - a route helyesen ad 204-et
    #  - a törlés ténylegesen érvényesült

    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/tasks",
                json={
                    "title": "Törlendő task",
                    "description": "Ezt törölni fogjuk",
                    "status": "todo",
                },
            )

            assert create_response.status_code == 201
            created_task = create_response.json()
            task_id = created_task["id"]

            delete_response = client.delete(f"/api/v1/tasks/{task_id}")
            assert delete_response.status_code == 204

            get_response = client.get(f"/api/v1/tasks/{task_id}")

        assert get_response.status_code == 404
        assert get_response.json() == {"detail": "Task not found"}
    finally:
        app.dependency_overrides.clear()


def test_create_task_with_empty_title_returns_422() -> None:
    memory_repo = TaskRepoMemory()

    def override_get_service() -> TaskService:
        return TaskService(memory_repo)

    app.dependency_overrides[get_service] = override_get_service

    # Ellenőrzi, hogy az input validáció tényleg működik.
    # Mivel a TaskCreate modelledben ez van:
    # title: str = Field(min_length=1, max_length=200)
    # ezért az üres string érvénytelen. (422 Unprocessable Entity)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/tasks",
                json={
                    "title": "",
                    "description": "Érvénytelen task",
                    "status": "todo",
                },
            )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
