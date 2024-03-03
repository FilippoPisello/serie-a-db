import pytest

from serie_a_db import DEFINITIONS_DIR
from serie_a_db.update import DefinitionQuery
from tests.test_utils import strings_equivalent


def test_queries_in_definitions_respect_the_standard_format():
    """All queries in the definitions directory respect the standard format."""
    for file in DEFINITIONS_DIR.iterdir():
        if file.suffix == ".sql":
            DefinitionQuery.from_definitions(file.stem)


class TestSingleQuery:
    """Case when there is only one query in the file.

    This assumes that there is no difference between the staging and the prod
    table, thus both the staging table and the statement to insert data from
    the staging to the prod table can be derived from the prod table itself.
    """

    def test_if_expected_creation_statement_missing_then_error(self):
        query = "SELECT * FROM table"
        with pytest.raises(ValueError):
            DefinitionQuery(query=query, name="dm_table")

    def test_prod_query_is_query_itself(self):
        query = """CREATE TABLE IF NOT EXISTS dm_table (
            note
        );"""
        assert DefinitionQuery(query=query, name="dm_table").prod == query

    def test_staging_query_is_derived_from_prod_query(self):
        query = """CREATE TABLE IF NOT EXISTS dm_table (
            note
        );"""
        expected = """CREATE TABLE dm_table_staging (
            note
        );"""
        assert strings_equivalent(
            DefinitionQuery(query=query, name="dm_table").staging, expected
        )

    def test_insert_statement_is_derived_from_prod_query_one_column(self):
        query = """CREATE TABLE IF NOT EXISTS dm_table (
            note
        );"""

        expected = """
        INSERT INTO dm_table
        SELECT note FROM dm_table_staging
        ON CONFLICT DO UPDATE
        SET note = excluded.note;
        """

        assert strings_equivalent(
            DefinitionQuery(query=query, name="dm_table").insert, expected
        )

    def test_insert_statement_is_derived_from_prod_query_multiple_columns(self):
        query = """CREATE TABLE IF NOT EXISTS dm_table (
            note, date
        );"""

        expected = """
        INSERT INTO dm_table
        SELECT note, date FROM dm_table_staging
        ON CONFLICT DO UPDATE
        SET note = excluded.note,
            date = excluded.date;
        """

        assert strings_equivalent(
            DefinitionQuery(query=query, name="dm_table").insert, expected
        )


class TestMoreThanOneQuery:
    """Case when there are more than one query in the file.

    In this case, there must be at least three queries: one for the staging
    table, one for the prod table and one for the insert statement.

    The "at least" derives from the fact that the insert statement can be
    broken down into multiple queries.
    """

    def test_if_staging_and_prod_statement_are_swapped_then_error(self):
        """The prod table must have the IF NOT EXISTS clause."""
        query = """
        CREATE TABLE IF NOT EXISTS dm_table_staging (
            note
        );

        CREATE TABLE dm_table (
            note
        );

        INSERT INTO dm_table
        SELECT note FROM dm_table_staging
        ON CONFLICT DO UPDATE
        SET note = excluded.note;
        """
        with pytest.raises(ValueError):
            DefinitionQuery(query=query, name="dm_table")

    def test_if_two_queries_then_error(self):
        query = """
        CREATE TABLE IF NOT EXISTS dm_table_staging (
            note
        );

        CREATE TABLE IF NOT EXISTS dm_table (
            note
        );
        """
        with pytest.raises(ValueError):
            DefinitionQuery(query=query, name="dm_table")

    def test_if_three_queries_but_no_insert_then_error(self):
        query = """
        CREATE TABLE IF NOT EXISTS dm_table (
            note
        );

        CREATE TABLE dm_table_staging (
            note
        );

        CREATE TABLE IF NOT EXISTS dm_table_2 (
            note
        );
        """
        with pytest.raises(ValueError) as exc_info:
            DefinitionQuery(query=query, name="dm_table")

        assert "none of them is an INSERT statement." in str(exc_info.value)

    def test_if_three_queries_as_expected_then_no_error(self):
        query = """
        CREATE TABLE IF NOT EXISTS dm_table (
            note
        );

        CREATE TABLE dm_table_staging (
            a_note
        );

        INSERT INTO dm_table
        SELECT a_note FROM dm_table_staging
        ON CONFLICT DO UPDATE
        SET note = excluded.a_note;
        """
        assert strings_equivalent(
            DefinitionQuery(query=query, name="dm_table").prod,
            """CREATE TABLE IF NOT EXISTS dm_table (
                note
            );""",
        )
        assert strings_equivalent(
            DefinitionQuery(query=query, name="dm_table").staging,
            """CREATE TABLE dm_table_staging (
            a_note
            );""",
        )
        assert strings_equivalent(
            DefinitionQuery(query=query, name="dm_table").insert,
            """
            INSERT INTO dm_table
            SELECT a_note FROM dm_table_staging
            ON CONFLICT DO UPDATE
            SET note = excluded.a_note;
            """,
        )
