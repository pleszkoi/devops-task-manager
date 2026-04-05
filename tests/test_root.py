# importálja a FastAPI teszt kliensét.
# A TestClient lehetővé teszi, hogy HTTP kéréseket küldjünk az appnak, anélkül, hogy külön uvicorn szervert kellene indítani.

from fastapi.testclient import TestClient

from devops_task_manager.core.config import settings

# importálja a FastAPI app objektumot a main.py-ból.
# Ez ugyanaz az app, amit normál esetben az uvicorn is használna.
# Fontos, hogy most már a lifespan is ide tartozik, ezért különösen jó a TestClient-et with blokkban használni.

from devops_task_manager.main import app

# Ez maga a tesztfüggvény.
# A pytest automatikusan felismeri, mert:
#  - a fájlnév test_...
#  - a függvénynév is test_...

def test_root() -> None:

    # létrehoz egy tesztkliens példányt.
    # A with blokk azért jó, mert:
    #  - a kliens inicializálja az appot,
    #  - lefuttatja az alkalmazás lifecycle részét,
    #  - és a blokk végén rendesen lezárja azt.

    with TestClient(app) as client:

        # elküld egy GET kérést a root endpointnak.

        response = client.get("/")
    
    # ellenőrzi, hogy a HTTP státuszkód 200 OK.
    # Ha nem 200, a teszt elbukik.

    assert response.status_code == 200

    # ellenőrzi a teljes JSON választ.
    # A response.json() Python dictet ad vissza, amit összehasonlítasz az elvárt értékkel.

    assert response.json() == {
        "app": settings.app_name,
        "env": settings.app_env,
        "version": settings.app_version,
    }
