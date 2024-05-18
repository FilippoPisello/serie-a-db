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
            dummy_name INTEGER
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
        "CREATE TABLE IF NOT EXISTS dm_dummy (dummy_name INTEGER);",
        "INSERT INTO dm_dummy VALUES (5);",
    )

    # Act
    builder = DbUpdater(db, {"dm_dummy": table})
    builder.update_all_tables()

    # Assert
    assert db.get_all_rows("ft_tables_update") == [
        ("dm_dummy", "2024-01-01 12:00:00.000", 1)
    ]


def test_db_update_one_table(db):
    # Arrange
    table = WarehouseTable(
        "dm_dummy",
        "CREATE TABLE IF NOT EXISTS dm_dummy (dummy_name INTEGER);",
        "INSERT INTO dm_dummy VALUES (5);",
    )

    # Act
    builder = DbUpdater(db, {"dm_dummy": table})
    builder.update_all_tables()

    # Assert
    assert db.count_rows("dm_dummy") == 1
    assert [("dm_dummy",)] == db.select("SELECT table_name FROM ft_tables_update")


def test_db_update_two_independent_tables(db):
    # Arrange
    def_statement = "CREATE TABLE IF NOT EXISTS dm_dummy1 (dummy_name INTEGER);"
    insert_statement = "INSERT INTO dm_dummy1 VALUES (5);"
    table1 = WarehouseTable(
        "dm_dummy1",
        def_statement,
        insert_statement,
    )
    table2 = WarehouseTable(
        "dm_dummy2",
        def_statement.replace("dm_dummy1", "dm_dummy2"),
        insert_statement.replace("dm_dummy1", "dm_dummy2"),
    )

    # Act
    builder = DbUpdater(db, {"dm_dummy1": table1, "dm_dummy2": table2})
    builder.update_all_tables()

    # Assert
    assert db.count_rows("dm_dummy1") == db.count_rows("dm_dummy2") == 1
    assert [("dm_dummy1",), ("dm_dummy2",)] == db.select(
        "SELECT table_name FROM ft_tables_update"
    )


def test_db_update_dep_lev_1_tables_one_layer(db):
    """Update order: source -> dependent."""
    # Arrange
    base = WarehouseTable(
        "dm_base",
        "CREATE TABLE IF NOT EXISTS dm_base (dummy_name INTEGER);",
        "INSERT INTO dm_base VALUES (5);",
    )
    # The second table depends on the first one
    dependent = WarehouseTable(
        "dm_dep_lev_1",
        "CREATE TABLE IF NOT EXISTS dm_dep_lev_1 (dummy_name INTEGER);",
        "INSERT INTO dm_dep_lev_1 SELECT * FROM dm_base;",
    )

    # Act
    builder = DbUpdater(db, {"dm_base": base, "dm_dep_lev_1": dependent})
    builder.update_all_tables()

    # Assert
    assert db.meta.last_updated("dm_dep_lev_1") > db.meta.last_updated("dm_base")


def test_db_update_dep_lev_1_tables_two_layers(db):
    """Update order: source -> dependent -> dependent-dependent."""
    # Arrange
    base = WarehouseTable(
        "dm_base",
        "CREATE TABLE IF NOT EXISTS dm_base (dummy_name INTEGER);",
        "INSERT INTO dm_base VALUES (5);",
    )
    dependent = WarehouseTable(
        "dm_dep_lev_1",
        "CREATE TABLE IF NOT EXISTS dm_dep_lev_1 (dummy_name INTEGER);",
        "INSERT INTO dm_dep_lev_1 SELECT * FROM dm_base;",
    )
    dep_lev_2 = WarehouseTable(
        "dm_dep_lev_2",
        "CREATE TABLE IF NOT EXISTS dm_dep_lev_2 (dummy_name INTEGER);",
        "INSERT INTO dm_dep_lev_2 SELECT * FROM dm_dep_lev_1;",
    )

    # Act
    builder = DbUpdater(
        db,
        {
            "dm_base": base,
            "dm_dep_lev_1": dependent,
            "dm_dep_lev_2": dep_lev_2,
        },
    )
    builder.update_all_tables()

    # Assert
    assert db.meta.last_updated("dm_dep_lev_1") > db.meta.last_updated("dm_base")
    assert db.meta.last_updated("dm_dep_lev_2") > db.meta.last_updated("dm_dep_lev_1")
