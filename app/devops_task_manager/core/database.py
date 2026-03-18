# Ez hozza létre a SQLAlchemy engine objektumot.
# Az engine szerepe:
# ez a központi objektum, ami tudja, hogyan kell az adatbázissal kommunikálni
# Nem maga a konkrét SQL query, hanem inkább a kapcsolatkezelő infrastruktúra.

from sqlalchemy import create_engine

# sessionmaker: 
# Nem sessiont ad közvetlenül, hanem egy olyan objektumot, amiből később sessionöket lehet létrehozni
# db = SessionLocal()
#
# DeclarativeBase:
# Ez az SQLAlchemy ORM modellek alap osztálya.
# Erre fog épülni például a TaskDB modell.

from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Ez a config.py-ból jön. Innen kapjuk meg a kapcsolat stringet

from devops_task_manager.core.config import settings

# Ez lesz az összes adatbázis modell közös alaposztálya.
# A Base gyűjti össze az ORM modelleket.
#
# Amikor később ezt hívjuk: Base.metadata.create_all(bind=engine)
# akkor a SQLAlchemy végignézi:
#  - milyen modellek öröklik a Base-t
#  - azokból milyen táblákat kell csinálni
# Tehát a Base tulajdonképpen a modellek közös regisztere.

class Base(DeclarativeBase):
    pass

# Az engine a DB kapcsolatkezelés központi objektuma.
# Az engine:
#  - tudja, milyen adatbázishoz csatlakozol
#  - tud kapcsolatokat nyitni
#  - kapcsolatokat újrahasznosít
#  - query-ket tud végrehajtani
#  - a háttérben connection poolt kezel

engine = create_engine(
    
    # Ez a config.py-ban összeállított kapcsolat string.
    
    settings.database_url, 

    # Ez azt mondja: ne logolja ki a SQLAlchemy minden SQL lekérdezését a konzolra
    # Ha True lenne, akkor a logokban lehetne látni az SQL utasításokat, például: SELECT tasks.id, tasks.title FROM tasks

    echo=False, 

    # Ez azt csinálja: mielőtt SQLAlchemy újrahasznál egy meglévő DB kapcsolatot a poolból, ellenőrzi, hogy él-e még
    #
    # Az engine a háttérben kapcsolat poolt tart fenn.
    # A pool lényege:
    #  - ne kelljen minden queryhez teljesen új TCP kapcsolatot nyitni
    #  - a meglévőket újra lehet használni
    #  - gyorsabb és hatékonyabb
    #
    # Ha a Postgres pod újraindul, akkor a régi kapcsolatok halottak lesznek.
    # A pool_pre_ping=True segít, hogy ezek ne okozzanak újra és újra hibát.
    
    pool_pre_ping=True,
)

# Ez egy session factory.
# a SessionLocal nem session, hanem session-készítő
# Tehát ez még nem nyit DB kapcsolatot önmagában.
# Majd amikor ezt írjuk:
# db = SessionLocal()
# akkor kapunk egy konkrét SQLAlchemy sessiont.

SessionLocal = sessionmaker(

    # Ez azt jelenti, hogy ez a session factory ehhez az engine-hez tartozik
    # Vagyis az innen készített sessionök a settings.database_url alapján létrehozott DB kapcsolatot fogják használni.

    bind=engine, 
    
    # Az autoflush azt szabályozza, hogy a session automatikusan “kitolja-e” a változásokat az adatbázis felé bizonyos műveletek előtt.
    # Most ezt kikapcsoljuk, mert egyszerűbb és kiszámíthatóbb.
    # Ez azt jelenti, hogy a változtatások jellemzően akkor mennek ténylegesen a DB-be, amikor ezt hívjuk:
    # db.commit()
    
    autoflush=False, 
    
    # Ez azt jelenti, hogy a session nem commitol automatikusan minden művelet után
    # Vagyis ha létrehozunk egy új rekordot: 
    # db.add(task)
    # az még nem biztos, hogy az adatbázisban van.
    # Csak akkor kerül be biztosan, amikor ezt meghívjuk:
    # db.commit()
    # Ez fontos, mert így kontrolláltan kezeled a tranzakciókat.
    
    autocommit=False,
)
