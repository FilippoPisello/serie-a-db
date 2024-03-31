from collections import namedtuple
from typing import NamedTuple

import pytest

from serie_a_db.db.db import Db
from serie_a_db.db.tables_update.table_update import DbTable


def test_table_name():
    """A DbTable subclass has a table name derived from its class name."""

    class DmSeason(DbTable):
        pass

    assert DmSeason.table_name() == "dm_season"

    class DmMatchDay(DbTable):
        pass

    assert DmMatchDay.table_name() == "dm_match_day"


class TestDataCompatibilityCheck:
    """Before-insert check for data compatibility with the table."""

    def test_error_if_data_incompatible(self):
        season = namedtuple("Season", ["season_id", "season_name"])
        data = [season(2021, "2021/22")]
        # The columns are in the wrong order
        columns = ("season_name", "season_id")
        with pytest.raises(ValueError):
            DbTable.error_if_data_incompatible(data, columns)

    def test_no_error_if_data_compatible(self):
        season = namedtuple("Season", ["season_id", "season_name"])
        data = [season(2021, "2021/22")]
        columns = ("season_id", "season_name")
        DbTable.error_if_data_incompatible(data, columns)


def test_update_is_logged_in_meta_table(db: Db, freeze_time):
    """Table updates are logged in a dedicated table."""
    # Arrange
    dummy = namedtuple("Dummy", ["dummy_id", "dummy_name"])
    records = [dummy(1, "dummy"), dummy(2, "dummy")]
    script = """CREATE TABLE IF NOT EXISTS dm_dummy (
            dummy_id INTEGER PRIMARY KEY,
            dummy_name
    );"""

    class DmDummy(DbTable):
        def extract_data(self) -> list[NamedTuple]:
            return records

    # Act
    DmDummy.from_string(db, script).update()

    # Assert
    assert db.get_all_rows("ft_tables_update") == [
        ("dm_dummy", "2024-01-01 12:00:00", len(records))
    ]
