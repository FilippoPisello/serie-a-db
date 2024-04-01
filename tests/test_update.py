from collections import namedtuple
from typing import NamedTuple

import pytest

from serie_a_db.db.db import Db
from serie_a_db.db.update_tables.table_updater import DbTable
from serie_a_db.exceptions import TableUpdateError


def test_table_name():
    """A DbTable subclass has a table name derived from its class name."""

    class DmSeason(DbTable):
        pass

    assert DmSeason.table_name() == "dm_season"

    class DmMatchDay(DbTable):
        pass

    assert DmMatchDay.table_name() == "dm_match_day"


def test_error_if_data_incompatible(db):
    # Arrange
    dummy = namedtuple("Season", ["season_id"])
    records = [dummy(1), dummy(2)]
    script_with_different_column = """CREATE TABLE IF NOT EXISTS dm_dummy (
            dummy_name INTEGER PRIMARY KEY
    );"""

    class DmDummy(DbTable):

        def extract_data(self, boundaries: dict) -> list[NamedTuple]:
            return records

    # Act & Assert
    with pytest.raises(TableUpdateError):
        DmDummy.from_string(db, script_with_different_column).update()


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

        def extract_data(self, boundaries: dict) -> list[NamedTuple]:
            return records

    # Act
    DmDummy.from_string(db, script).update()

    # Assert
    assert db.get_all_rows("ft_tables_update") == [
        ("dm_dummy", "2024-01-01 12:00:00", len(records))
    ]


def test_boundaries_are_used_in_extract_data(db: Db):
    """Boundaries are used in the data extraction."""
    # Arrange
    dummy = namedtuple("Dummy", ["dummy_id"])
    records = [dummy(1), dummy(2), dummy(3)]
    script = """CREATE TABLE IF NOT EXISTS dm_dummy (
            dummy_id INTEGER PRIMARY KEY
    );"""

    class DmDummy(DbTable):

        def establish_data_retrieval_boundaries(self) -> dict:
            return {"data": records}

        def extract_data(self, boundaries: dict) -> list[NamedTuple]:
            return boundaries["data"]

    # Act
    DmDummy.from_string(db, script).update()

    # Assert
    assert db.get_all_rows("dm_dummy") == [(1,), (2,), (3,)]
