# Ez vezeti be a 12-factor app konfigurációs modellt

# BaseSettings: egy speciális Pydantic osztály.
#
# A BaseSettings képes:
#  - környezeti változókból olvasni
#  - .env fájlból olvasni
#  - default értéket adni
#
# SettingsConfigDict: a Pydantic v2 konfigurációs mechanizmusa.

from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings: egy konfigurációs objektum.
# A FastAPI app minden konfigurációját itt fogjuk tárolni.

# Ez lesz például:
#  - app neve
#  - environment
#  - verzió
#  - később database URL
#  - log level
#  - feature flag-ek

class Settings(BaseSettings):

    # azt mondja a Pydanticnak: ne olvass .env fájlt
    # Miért? Mert Kubernetesben a konfiguráció environment variable formában jön.
    
    model_config = SettingsConfigDict(env_file=None)

    # Konfigurációs mezők:
    # app_name: str = "devops-task-manager" -> egy Pydantic field
    # str -> típus
    # "devops-task-manager" -> default érték
    #
    # Ezek később hasznosak:
    #  - logging
    #  - monitoring
    #  - debugging
    #  - Kubernetes rollout

    app_name: str = "devops-task-manager"
    app_env: str = "dev"
    app_version: str = "0.1.0"

# settings objektum
# Ez létrehozza a konfiguráció példányát.

# Ez történik:
#  - beolvassa az env varokat
#  - alkalmazza a defaultokat
#  - validálja a típusokat

# Ezután bárhol importálható

settings = Settings()
