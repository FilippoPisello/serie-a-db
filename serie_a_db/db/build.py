"""Logic to build the db."""

from serie_a_db import META_DIR
from serie_a_db.db.db import Db
from serie_a_db.db.update_tables import TABLES
from serie_a_db.db.update_tables.table_updater import DbTable


def create_meta_tables(db: Db) -> None:
    """Create the meta tables if they don't exist."""
    for file in META_DIR.iterdir():
        db.execute(file.read_text())
    return db.commit()


def update_db(db: Db, tables: tuple[type[DbTable]] = TABLES) -> None:
    """Update all the tables in the database."""
    for table in tables:
        table.from_definitions(db).update()
