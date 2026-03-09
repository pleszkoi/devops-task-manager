from fastapi import APIRouter
from devops_task_manager.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@router.get("/ready")
def ready():
    # Week2-ben: DB connectivity check ide jön.
    return {"status": "ready"}