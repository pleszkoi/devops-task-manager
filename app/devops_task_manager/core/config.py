# Ez vezeti be a 12-factor app konfigurációs modellt
# Vagyis: A konfiguráció a környezetből jön, nem a kódba van égetve

# BaseSettings: egy speciális Pydantic osztály, ami konfiguráció kezelésre való.
#
# A lényege, hogy nem kézzel kell os.getenv()-ezni minden értéket, hanem egy konfigurációs osztályból dolgozol

# A BaseSettings képes:
#  - környezeti változókból olvasni
#  - .env fájlból olvasni
#  - default értéket adni
#
# SettingsConfigDict: a Pydantic v2 konfigurációs mechanizmusa.

from pydantic_settings import BaseSettings, SettingsConfigDict

# Ez az alkalmazás központi konfigurációs objektuma.

# A szerepe:
#  - összegyűjti az app configot egy helyre
#  - típusosan leírja a mezőket
#  - env varból fel tudja tölteni őket
#  - később könnyen bővíthető
# A projektben ez a konfigurációs központ.

class Settings(BaseSettings):

    # Ez azt mondja: # ne próbálj .env fájlt olvasni
    # 
    # Kubernetesben a konfigurációt nem .env-ből akarjuk adni, hanem:
    #  - env mezőből a Deployment YAML-ben
    #  - később ConfigMapből
    #  - Secretből

    model_config = SettingsConfigDict(env_file=None)

    app_name: str = "devops-task-manager"
    app_env: str = "dev"
    app_version: str = "0.4.0"

    # a PostgreSQL kapcsolat paraméterezése.

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "taskdb"
    db_user: str = "taskuser"
    db_password: str = "taskpassword"

    # A property azt jelenti: úgy használhatod, mintha attribútum lenne, de valójában egy függvény számolja ki

    @property

    # a database.py majd ezt használja: engine = create_engine(settings.database_url, ...)
    # Tehát a teljes DB kapcsolat ezen a mezőn keresztül épül fel.

    def database_url(self) -> str:

        # pl.:     postgresql+psycopg://taskuser:taskpassword@localhost:5432/taskdb
        # K8s-ben: postgresql+psycopg://taskuser:taskpassword@postgres:5432/taskdb
        #
        # postgresql+psycopg://
        # Ez mondja a SQLAlchemynek:
        #  - adatbázis típus: PostgreSQL
        #  - driver: psycopg
        # 
        # {self.db_user}:{self.db_password}
        # Felhasználónév és jelszó
        #
        # @{self.db_host}:{self.db_port}
        # Host és port
        # 
        # /{self.db_name}
        # A konkrét adatbázis neve.

        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

# Ez létrehozza a konfiguráció példányát.
#
# Itt történik meg:
#  - env varok beolvasása
#  - default értékek alkalmazása
#  - típusok validálása
#  - a settings objektum létrejötte

# Ezután bárhol importálható és használható

settings = Settings()
