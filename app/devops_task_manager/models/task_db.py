# SQL típusok

from sqlalchemy import Integer, String

# Mapped:
# Ez egy type hint SQLAlchemy 2.0 stílusban.
# Nem kötelező runtime működéshez, de:
#  - segíti a típusellenőrzést
#  - segíti az IDE-t
#  - tisztább kódot ad
# 
# mapped_column:
# Ez az új SQLAlchemy 2.0 módja az oszlopok definiálásának.

from sqlalchemy.orm import Mapped, mapped_column

# Base:
# A database.py-ból jön.
# Ez kapcsolja a modellt az ORM rendszerhez.

from devops_task_manager.core.database import Base

# Ez egy ORM modell.
# A jelentése: ez az osztály egy adatbázis táblát reprezentál

class TaskDB(Base):

    # PostgreSQL-ben létrejön: tasks

    __tablename__ = "tasks"

    # id: Mapped[int]
    # Ez type hint: ez egy int típusú mező
    #
    # mapped_column(Integer, ...)
    # Ez egy adatbázis oszlop.
    #
    # primary_key=True
    # Ez az elsődleges kulcs.
    #
    # index=True
    # Ez külön indexet is létrehoz.
    # Gyorsítja a lekérdezéseket

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # nullable=False -> Ez azt jelenti: NOT NULL, tehát a mező kötelező.
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # str | None -> Ez Python union type: lehet string vagy None
    
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="todo")
    
# A SQLAlchemy ezt generálja (egyszerűsítve):
# 
# CREATE TABLE tasks (
#     id SERIAL PRIMARY KEY,
#     title VARCHAR(200) NOT NULL,
#     description VARCHAR(2000),
#     status VARCHAR(20) NOT NULL DEFAULT 'todo'
# );
