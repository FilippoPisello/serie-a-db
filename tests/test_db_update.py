import time
from collections import namedtuple
from typing import NamedTuple

from serie_a_db.db.build import update_db
from serie_a_db.db.update_tables.table_updater import DbTable

# Defining three DbTable for testing, having the same behavior but different
# name
dummy_record = namedtuple("Dummy", "dummy_name")
dummy_script = """CREATE TABLE IF NOT EXISTS dm_dummy1 (
            dummy_name VARCHAR
    );"""


class DmDummy1(DbTable):
    def extract_data(self, boundaries: dict) -> list[NamedTuple]:  # noqa
        time.sleep(0.001)  # Sleep or too quick and cannot differentiate update ts
        return [dummy_record("dummy")]


class DmDummy2(DbTable):
    def extract_data(self, boundaries: dict) -> list[NamedTuple]:  # noqa
        time.sleep(0.001)
        return [dummy_record("dummy")]


class DmDummy3(DbTable):
    def extract_data(self, boundaries: dict) -> list[NamedTuple]:  # noqa
        time.sleep(0.001)
        return [dummy_record("dummy")]


def test_db_update_one_table(db):
    # Arrange
    instantiated_tables = [DmDummy1.from_string(db, dummy_script)]

    # Act
    update_db(db, instantiated_tables)

    # Assert
    assert db.count_rows("dm_dummy1") == 1
    assert [("dm_dummy1",)] == db.select("SELECT table_name FROM ft_tables_update")


def test_db_update_two_independent_tables(db):
    # Arrange
    instantiated_tables = [
        DmDummy1.from_string(db, dummy_script),
        DmDummy2.from_string(db, dummy_script.replace("dm_dummy1", "dm_dummy2")),
    ]

    # Act
    update_db(db, instantiated_tables)

    # Assert
    assert db.count_rows("dm_dummy1") == db.count_rows("dm_dummy2") == 1
    assert [("dm_dummy1",), ("dm_dummy2",)] == db.select(
        "SELECT table_name FROM ft_tables_update"
    )


def test_db_update_dependent_tables_one_layer(db):
    """Dependent table is updated last."""
    # Arrange
    DmDummy1.DEPENDS_ON = [DmDummy2]
    instantiated_tables = [
        DmDummy1.from_string(db, dummy_script),
        DmDummy2.from_string(db, dummy_script.replace("dm_dummy1", "dm_dummy2")),
    ]

    # Act
    update_db(db, instantiated_tables)

    # Assert
    assert db.last_updated("dm_dummy1") > db.last_updated("dm_dummy2")


def test_db_update_dependent_tables_two_layers(db):
    """Dependent table is updated last."""
    # Arrange
    DmDummy1.DEPENDS_ON = [DmDummy2]
    DmDummy2.DEPENDS_ON = [DmDummy3]
    instantiated_tables = [
        DmDummy1.from_string(db, dummy_script),
        DmDummy2.from_string(db, dummy_script.replace("dm_dummy1", "dm_dummy2")),
        DmDummy3.from_string(db, dummy_script.replace("dm_dummy1", "dm_dummy3")),
    ]

    # Act
    update_db(db, instantiated_tables)

    # Assert
    assert db.last_updated("dm_dummy1") > db.last_updated("dm_dummy2")
    assert db.last_updated("dm_dummy2") > db.last_updated("dm_dummy3")
