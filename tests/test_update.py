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


DUMMY_INPUT = namedtuple("Season", ["season_id"])
DUMMY_RECORDS = [DUMMY_INPUT(1), DUMMY_INPUT(2)]


def test_error_if_data_incompatible(db):
    # Arrange
    script_with_different_column = """CREATE TABLE IF NOT EXISTS dm_dummy (
            dummy_name INTEGER PRIMARY KEY
    );"""

    class DmDummy(DbTable):

        def extract_data(self, boundaries: dict) -> list[NamedTuple]:  # noqa
            return DUMMY_RECORDS

    # Act & Assert
    with pytest.raises(TableUpdateError):
        DmDummy.from_string(db, script_with_different_column).update()


def test_update_is_logged_in_meta_table(db: Db, freeze_time):
    """Table updates are logged in a dedicated table."""
    # Arrange
    script = """CREATE TABLE IF NOT EXISTS dm_dummy (
            season_id INTEGER PRIMARY KEY
    );"""

    class DmDummy(DbTable):

        def extract_data(self, boundaries: dict) -> list[NamedTuple]:  # noqa
            return DUMMY_RECORDS

    # Act
    DmDummy.from_string(db, script).update()

    # Assert
    assert db.get_all_rows("ft_tables_update") == [
        ("dm_dummy", "2024-01-01 12:00:00", len(DUMMY_RECORDS))
    ]


def test_boundaries_are_used_in_extract_data(db: Db):
    """Boundaries are used in the data extraction."""
    # Arrange
    script = """CREATE TABLE IF NOT EXISTS dm_dummy (
            season_id INTEGER PRIMARY KEY
    );"""

    class DmDummy(DbTable):

        def establish_data_retrieval_boundaries(self) -> dict:
            return {"data": DUMMY_RECORDS}

        def extract_data(self, boundaries: dict) -> list[NamedTuple]:
            return boundaries["data"]

    # Act
    DmDummy.from_string(db, script).update()

    # Assert
    assert db.get_all_rows("dm_dummy") == DUMMY_RECORDS
