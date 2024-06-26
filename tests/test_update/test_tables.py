from serie_a_db.data_extraction.table_specific_extractors.dm_match_day import MatchDay
from serie_a_db.db.client import Db
from serie_a_db.db.table import StagingTable as St
from serie_a_db.db.table import WarehouseTable as Wt
from serie_a_db.db.update import DbUpdater


def test_dm_season_update(db: Db):
    """Test the update of the dm_season table."""
    # Arrange
    match_day_data = [
        # One completed record for season 2023
        MatchDay.fake(
            season_code_serie_a_api=23,
            season_year_start=2023,
            status="completed",
        ).to_namedtuple(),
        # One completed and one ongoing record for season 2024
        MatchDay.fake(
            season_code_serie_a_api=24,
            season_year_start=2024,
            status="completed",
        ).to_namedtuple(),
        MatchDay.fake(
            season_code_serie_a_api=24,
            season_year_start=2024,
            status="ongoing",
        ).to_namedtuple(),
    ]
    test_schema = {
        "dm_season": Wt.from_file("dm_season"),
        "dm_match_day_staging": St.from_file(
            "dm_match_day_staging", lambda: match_day_data
        ),
    }

    # Act
    updater = DbUpdater(db, test_schema)
    updater.update_table_and_upstream_dependencies(test_schema["dm_season"])

    # Assert
    assert db.get_all_rows("dm_season") == [
        ("S23", "S23-24", 23, 2023, 2024, "completed"),
        ("S24", "S24-25", 24, 2024, 2025, "ongoing"),
    ]


def test_dm_match_day_update(db: Db):
    # Arrange
    match_day_data = [
        # One completed record for season 2023
        MatchDay(
            season_code_serie_a_api=23,
            season_year_start=2023,
            status="completed",
            code_serie_a_api=231,
            number=1,
        ).to_namedtuple(),
        # One completed and one ongoing record for season 2024
        MatchDay(
            season_code_serie_a_api=24,
            season_year_start=2024,
            status="completed",
            code_serie_a_api=241,
            number=1,
        ).to_namedtuple(),
        MatchDay(
            season_code_serie_a_api=24,
            season_year_start=2024,
            status="ongoing",
            code_serie_a_api=242,
            number=2,
        ).to_namedtuple(),
    ]
    test_schema = {
        "dm_season": Wt.from_file("dm_season"),
        "dm_match_day_staging": St.from_file(
            "dm_match_day_staging", lambda: match_day_data
        ),
        "dm_match_day": Wt.from_file("dm_match_day"),
    }

    # Act
    updater = DbUpdater(db, test_schema)
    updater.update_table_and_upstream_dependencies(test_schema["dm_match_day"])

    # Assert
    assert db.count_rows("dm_match_day") == len(match_day_data)
    assert db.get_all_rows("dm_match_day") == [
        ("S23M01", "S23", "S23-24 MD01", 231, 1, "completed"),
        ("S24M01", "S24", "S24-25 MD01", 241, 1, "completed"),
        ("S24M02", "S24", "S24-25 MD02", 242, 2, "ongoing"),
    ]
