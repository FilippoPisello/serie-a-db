"""Schema for the Serie A database."""

from serie_a_db.data_extraction.table_specific_extractors.dm_season import (
    scrape_dm_season_data,
)
from serie_a_db.db.table import DbTable
from serie_a_db.db.table import StagingTable as St
from serie_a_db.db.table import WarehouseTable as Pt

TABLES: dict[str, DbTable] = {
    "dm_season": Pt.from_file("dm_season"),
    "dm_season_staging": St.from_file("dm_season_staging", scrape_dm_season_data),
}