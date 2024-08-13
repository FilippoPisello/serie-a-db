"""Schema for the Serie A database."""

# noqa: E501
from serie_a_db.data_extraction.table_specific_extractors.st_fm_player import (
    scrape_player_data as scrape_player_data_fm,
)
from serie_a_db.data_extraction.table_specific_extractors.st_fpi_player import (
    scrape_player_data as scrape_player_data_fpi,
)
from serie_a_db.data_extraction.table_specific_extractors.st_fpi_player_match import (
    scrape_player_match_data,
)
from serie_a_db.data_extraction.table_specific_extractors.st_match import (
    scrape_match_data,
)
from serie_a_db.data_extraction.table_specific_extractors.st_match_day import (
    scrape_match_day_data,
)
from serie_a_db.data_extraction.table_specific_extractors.st_player_cross_source_mapping import (
    derive_mappings,
)
from serie_a_db.db.table import DbTable
from serie_a_db.db.table import StagingTable as St
from serie_a_db.db.table import WarehouseTable as Wt

TABLES: dict[str, DbTable] = {
    # Warehouse tables
    "dm_season": Wt.from_file("dm_season"),
    "dm_match_day": Wt.from_file("dm_match_day"),
    "dm_team": Wt.from_file("dm_team"),
    "dm_coach": Wt.from_file("dm_coach"),
    "ft_match": Wt.from_file("ft_match"),
    # Staging tables
    "st_match_day": St.from_file("st_match_day", scrape_match_day_data),
    "st_match": St.from_file("st_match", scrape_match_data),
    "st_fpi_player": St.from_file("st_fpi_player", scrape_player_data_fpi),
    "st_fm_player": St.from_file("st_fm_player", scrape_player_data_fm),
    "st_fpi_player_match": St.from_file(
        "st_fpi_player_match", scrape_player_match_data
    ),
    "st_player_cross_source_mapping": St.from_file(
        "st_player_cross_source_mapping",
        derive_mappings,
    ),
}
