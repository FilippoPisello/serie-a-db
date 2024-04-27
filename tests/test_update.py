from collections import namedtuple

import pytest

from serie_a_db.db.db import Db
from serie_a_db.db.update_tables import StagingTable
from serie_a_db.exceptions import TableUpdateError

DUMMY_INPUT = namedtuple("Season", ["season_id"])
DUMMY_RECORDS = [DUMMY_INPUT(1), DUMMY_INPUT(2)]


def test_error_if_data_incompatible(db):
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
    assert False


def test_boundaries_are_used_in_extract_data(db: Db):
    """Boundaries are used in the data extraction."""
    assert False
