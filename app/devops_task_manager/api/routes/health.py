from fastapi import APIRouter, HTTPException

# SQLAlchemy segédfüggvény nyers SQL-hez.
from sqlalchemy import text

from devops_task_manager.core.config import settings
from devops_task_manager.core.database import SessionLocal

router = APIRouter(tags=["health"])

# Ha a FastAPI process él és el tudja futtatni ezt a függvényt, akkor visszaad egy 200-as JSON választ.
@router.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }

# A readiness jelentése: képes-e az app valóban requesteket kiszolgálni
@router.get("/ready")
def ready():
    db = SessionLocal()
    try:
        # SELECT 1, mert ez a legegyszerűbb lehetséges query.
        # Nem függ egy konkrét táblától, nem kell hozzá adat, csak azt bizonyítja, hogy:
        #  - a kapcsolat felépült
        #  - a DB válaszol
        #  - a query futtatható

        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")
    finally:
        db.close()
