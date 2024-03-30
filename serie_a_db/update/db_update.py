"""Logic to update the database."""

from serie_a_db.db_setup import Db
from serie_a_db.update.dm_season import DmSeason

TABLES = [DmSeason]


def update_db(db: Db) -> None:
    """Update the database."""
    for table in TABLES:
        loaded_table = table.from_definitions(db)
        loaded_table.update()
