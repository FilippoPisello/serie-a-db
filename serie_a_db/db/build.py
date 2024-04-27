"""Logic to build the db."""

from serie_a_db import META_DIR
from serie_a_db.db.db import Db
from serie_a_db.db.update_tables import TABLES
from serie_a_db.utils import now


def create_meta_tables(db: Db) -> None:
    """Create the meta tables if they don't exist."""
    for file in META_DIR.iterdir():
        db.execute(file.read_text())
    return db.commit()


def update_db(db: Db) -> None:
    """Update all the tables in the database."""
    for table in TABLES:
        loaded_table = table.from_definitions(db)
        loaded_table.update()


def log_update_in_meta_table(db: Db, table_name: str) -> None:
    """Log the update on the ft_tables_update."""
    n_rows = db.count_rows(table_name)

    db.execute(
        """
        INSERT INTO ft_tables_update(table_name, datetime_updated, rows_number)
        VALUES(?, ?, ?);
        """,
        (table_name, now().strftime("%Y-%m-%d %H:%M:%S"), n_rows),
    )
