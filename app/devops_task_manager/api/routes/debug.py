import os
import socket
from fastapi import APIRouter
from devops_task_manager.core.config import settings

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/podinfo")
def podinfo():
    return {
        "hostname": socket.gethostname(),
        "pod_name_hint": os.getenv("HOSTNAME", ""),
        "app_env": settings.app_env,
        "version": settings.app_version,
    }