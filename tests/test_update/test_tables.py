from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import MatchDay
from serie_a_db.data_extraction.table_specific_extractors.dm_season import Season
from serie_a_db.db.client import Db
from serie_a_db.db.table import StagingTable as St
from serie_a_db.db.table import WarehouseTable as Wt
from serie_a_db.db.update import DbUpdater


def test_dm_season_update(db: Db):
    """Test the update of the dm_season table."""
    # Arrange
    data = [
        Season(year_start=2023, code_serie_a_api=23, active=1).to_namedtuple(),
        Season(year_start=2022, code_serie_a_api=22, active=0).to_namedtuple(),
    ]
    test_schema = {
        "dm_season": Wt.from_file("dm_season"),
        "dm_season_staging": St.from_file("dm_season_staging", lambda: data),
    }

    # Act
    updater = DbUpdater(db, test_schema)
    updater.update_table_and_upstream_dependencies(test_schema["dm_season"])

    # Assert
    assert db.count_rows("dm_season") == len(data)
    assert db.get_all_rows("dm_season") == [
        ("S23", "S23-24", 23, 2023, 2024, 1),
        ("S22", "S22-23", 22, 2022, 2023, 0),
    ]


def test_dm_match_day_update(db: Db):
    # Arrange
    match_day_data = [
        MatchDay(
            season_code_serie_a_api=23,
            code_serie_a_api=231,
            number=1,
            status="completed",
        ).to_namedtuple(),
    ]
    season_data = [
        Season(year_start=2023, code_serie_a_api=23, active=1).to_namedtuple(),
    ]
    test_schema = {
        "dm_match_day": Wt.from_file("dm_match_day"),
        "dm_match_day_staging": St.from_file(
            "dm_match_day_staging", lambda: match_day_data
        ),
        "dm_season": Wt.from_file("dm_season"),
        "dm_season_staging": St.from_file("dm_season_staging", lambda: season_data),
    }

    # Act
    updater = DbUpdater(db, test_schema)
    updater.update_table_and_upstream_dependencies(test_schema["dm_match_day"])

    # Assert
    assert db.count_rows("dm_match_day") == len(match_day_data)
    assert db.get_all_rows("dm_match_day") == [
        ("S23M01", "S23", "S23-24 MD01", 231, 1, "completed"),
    ]
