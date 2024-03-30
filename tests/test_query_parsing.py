import pytest

from serie_a_db import DEFINITIONS_DIR
from serie_a_db.update import DefinitionScript
from tests.test_utils import strings_equivalent


def test_queries_in_definitions_respect_the_standard_format():
    """All queries in the definitions directory respect the standard format."""
    for file in DEFINITIONS_DIR.iterdir():
        if file.suffix == ".sql":
            DefinitionScript.from_definitions(file.stem)


class TestSingleStatement:
    """Case when there is only one statement in the file.

    This assumes that there is no difference between the staging and the prod
    table, thus both the staging table and the statement to insert data from
    the staging to the prod table can be derived from the prod table itself.
    """

    def test_if_expected_creation_statement_missing_then_error(self):
        script = "SELECT * FROM table"
        with pytest.raises(ValueError):
            DefinitionScript(script=script, name="dm_table")

    def test_prod_statement_is_statement_itself(self):
        script = """CREATE TABLE IF NOT EXISTS dm_table (
            note
        );"""
        assert (
            DefinitionScript(script=script, name="dm_table").create_prod_table == script
        )

    def test_staging_statement_is_derived_from_prod_statement(self):
        script = """CREATE TABLE IF NOT EXISTS dm_table (
            note
        );"""
        expected = """CREATE TABLE dm_table_staging (
            note
        );"""
        assert strings_equivalent(
            DefinitionScript(script=script, name="dm_table").create_staging_table,
            expected,
        )

    @pytest.mark.parametrize(
        ("prod_script", "expected"),
        (
            (  # One column
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note
                );""",
                """INSERT INTO dm_table
                SELECT note FROM dm_table_staging
                WHERE true -- Disambiguates the following ON from potential JOIN ON
                ON CONFLICT DO UPDATE
                SET note = excluded.note;
                """,
            ),
            (  # Multiple columns
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date
                );""",
                """INSERT INTO dm_table
                SELECT note, date FROM dm_table_staging
                WHERE true -- Disambiguates the following ON from potential JOIN ON
                ON CONFLICT DO UPDATE
                SET note = excluded.note,
                    date = excluded.date;
                """,
            ),
        ),
    )
    def test_insert_statement_is_derived_from_prod_statement(
        self, prod_script, expected
    ):
        definition_script = DefinitionScript(script=prod_script, name="dm_table")
        assert strings_equivalent(
            definition_script.insert_from_staging_to_prod,
            expected,
        )

    @pytest.mark.parametrize(
        ("prod_script", "expected"),
        (
            (  # One column
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note
                );""",
                """INSERT INTO dm_table_staging(note)
                VALUES(?);""",
            ),
            (  # Multiple columns
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date
                );""",
                """INSERT INTO dm_table_staging(note, date)
                VALUES(?, ?);""",
            ),
        ),
    )
    def test_insert_values_into_staging_is_derived_from_prod_statement(
        self, prod_script, expected
    ):
        definition_script = DefinitionScript(script=prod_script, name="dm_table")
        assert strings_equivalent(
            definition_script.insert_values_into_staging,
            expected,
        )

    @pytest.mark.parametrize(
        ("prod_script", "expected_columns"),
        (
            (  # One column
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note
                );""",
                ("note",),
            ),
            (  # One column with CHECK clause containing a comma
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note CHECK (note IN ('a', 'b'))
                );""",
                ("note",),
            ),
            (  # Multiple columns
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date
                );""",
                ("note", "date"),
            ),
            (  # Multiple columns with first column having a CHECK clause
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note CHECK (note IN ('a', 'b')),
                    date
                );""",
                ("note", "date"),
            ),
            (  # Multiple columns with second column having a CHECK clause
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date CHECK (date IN ('a', 'b'))
                );""",
                ("note", "date"),
            ),
            (  # Multiple columns ending with a CHECK clause
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date,
                    CHECK (note IN ('a', 'b'))
                );""",
                ("note", "date"),
            ),
            (  # Multiple columns ending with a PRIMARY KEY clause
                """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date,
                    PRIMARY KEY (note)
                );""",
                ("note", "date"),
            ),
        ),
    )
    def test_prod_and_staging_columns_are_same_and_derived_from_prod_statement(
        self, prod_script, expected_columns
    ):
        definition_script = DefinitionScript(script=prod_script, name="dm_table")

        assert definition_script.prod_columns == definition_script.staging_columns
        assert definition_script.staging_columns == expected_columns


class TestMoreThanOneStatement:
    """Case when there are more than one statements in the file.

    In this case, there must be at least three queries: one for the staging
    table, one for the prod table and one for the insert statement.

    The "at least" derives from the fact that the insert statement can be
    broken down into multiple queries.
    """

    def test_if_staging_and_prod_statement_are_swapped_then_error(self):
        """The prod table must have the IF NOT EXISTS clause."""
        script = """
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
            DefinitionScript(script=script, name="dm_table")

    def test_if_two_queries_then_error(self):
        script = """
        CREATE TABLE IF NOT EXISTS dm_table_staging (
            note
        );

        CREATE TABLE IF NOT EXISTS dm_table (
            note
        );
        """
        with pytest.raises(ValueError):
            DefinitionScript(script=script, name="dm_table")

    def test_if_three_queries_but_no_insert_then_error(self):
        script = """
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
            DefinitionScript(script=script, name="dm_table")

        assert "none of them is an INSERT statement." in str(exc_info.value)

    def test_if_three_queries_as_expected_then_no_error(self):
        script = """
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
            DefinitionScript(script=script, name="dm_table").create_prod_table,
            """CREATE TABLE IF NOT EXISTS dm_table (
                note
            );""",
        )
        assert strings_equivalent(
            DefinitionScript(script=script, name="dm_table").create_staging_table,
            """CREATE TABLE dm_table_staging (
            a_note
            );""",
        )
        assert strings_equivalent(
            DefinitionScript(
                script=script, name="dm_table"
            ).insert_from_staging_to_prod,
            """
            INSERT INTO dm_table
            SELECT a_note FROM dm_table_staging
            ON CONFLICT DO UPDATE
            SET note = excluded.a_note;
            """,
        )

    @pytest.mark.parametrize(
        ("staging_statement", "expected"),
        (
            (  # One column
                """CREATE TABLE dm_table_staging (
                    a_note
                );""",
                """INSERT INTO dm_table_staging(a_note)
                VALUES(?);""",
            ),
            (  # Multiple columns
                """CREATE TABLE dm_table_staging (
                a_note,
                a_date
                );""",
                """INSERT INTO dm_table_staging(a_note, a_date)
                VALUES(?, ?);""",
            ),
        ),
    )
    def test_insert_values_into_staging_is_derived_from_staging_statement(
        self, staging_statement, expected
    ):
        script = f"""
        CREATE TABLE IF NOT EXISTS dm_table (
            note
        );

        {staging_statement}

        INSERT INTO dm_table
        SELECT a_note FROM dm_table_staging
        ON CONFLICT DO UPDATE
        SET note = excluded.a_note;
        """
        definition_script = DefinitionScript(script=script, name="dm_table")
        assert strings_equivalent(
            definition_script.insert_values_into_staging,
            expected,
        )
