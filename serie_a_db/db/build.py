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


def instantiate_tables(
    db: Db, tables: tuple[type[DbTable], ...] = TABLES
) -> tuple[DbTable, ...]:
    """Instantiate the DbTable objects."""
    return tuple(table.from_definitions(db) for table in tables)


def update_db(db: Db, tables: tuple[DbTable, ...]) -> None:
    """Update all the tables in the database."""
    for table in tables:
        _update_table_and_upstream_dependencies(db, table, tables)


def _update_table_and_upstream_dependencies(
    db: Db, table: DbTable, all_tables: tuple[DbTable, ...]
) -> None:
    """Update the passed table and its upstream dependencies.

    Dependencies are updated first.
    """
    for dependency in table.DEPENDS_ON:
        # Expect to find a single item
        instantiated_dependency = [
            tbl for tbl in all_tables if isinstance(tbl, dependency)
        ][0]
        _update_table_and_upstream_dependencies(db, instantiated_dependency, all_tables)
    table.update()
