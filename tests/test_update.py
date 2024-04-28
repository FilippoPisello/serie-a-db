from collections import namedtuple

import pytest

from serie_a_db.db.client import Db
from serie_a_db.db.table import StagingTable, WarehouseTable
from serie_a_db.db.update import DbUpdater
from serie_a_db.exceptions import TableUpdateError

DUMMY_INPUT = namedtuple("Season", ["season_id"])
DUMMY_RECORDS = [DUMMY_INPUT(1), DUMMY_INPUT(2)]


def test_error_if_data_being_inserted_does_not_match_table_columns(db):
    # Arrange
    script_with_different_column = """CREATE TABLE IF NOT EXISTS dm_dummy (
            dummy_name INTEGER PRIMARY KEY
    );"""

    table = StagingTable(
        "dm_dummy", script_with_different_column, lambda: DUMMY_RECORDS
    )

    # Act & Assert
    with pytest.raises(TableUpdateError):
        table.update(db)


def test_update_is_logged_in_meta_table(db: Db, freeze_time):
    """Table updates are logged in a dedicated table."""
    # Arrange
    table = WarehouseTable(
        "dm_dummy",
        "CREATE TABLE IF NOT EXISTS dm_dummy (dummy_name INTEGER PRIMARY KEY);",
        "INSERT INTO dm_dummy VALUES (5);",
    )

    # Act
    builder = DbUpdater(db, {"dm_dummy": table})
    builder.update_all_tables()

    # Assert
    assert db.get_all_rows("ft_tables_update") == [
        ("dm_dummy", "2024-01-01 12:00:00.000", 1)
    ]
