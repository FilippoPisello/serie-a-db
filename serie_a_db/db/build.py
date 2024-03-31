"""Logic to build the db."""

from serie_a_db import META_DIR
from serie_a_db.db.db import Db
from serie_a_db.db.tables_update import TABLES


def create_meta_tables(db: Db) -> None:
    """Create the meta tables if they don't exist."""
    for file in META_DIR.iterdir():
        db.execute(file.read_text())
    return db.commit()


def update_db(db: Db) -> None:
    """Update the database."""
    for table in TABLES:
        loaded_table = table.from_definitions(db)
        loaded_table.update()
