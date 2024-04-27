"""Logic to update tables in the database."""

from serie_a_db.db.update_tables.table_updater import CoreTable, StagingTable
from serie_a_db.db.update_tables.tables.dm_season import scrape_dm_season_data

TABLES = (
    CoreTable.from_file("dm_season"),
    StagingTable.from_file("dm_season_staging", scrape_dm_season_data),
)
TABLES_DICT = {table.name: table for table in TABLES}
