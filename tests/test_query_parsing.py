import pytest

from serie_a_db.exceptions import InvalidStatementError, NumberOfStatementsError
from serie_a_db.sql_parsing import (
    depends_on,
    derive_drop_table_statement,
    derive_populate_staging_statement,
    extract_attributes_from_create_statement,
    split_statements,
    validate_create_staging_statement,
    validate_create_statement_wh,
    validate_populate_statement_wh,
)
from tests.test_utils import strings_equivalent


class TestSplitStatements:

    @staticmethod
    @pytest.mark.parametrize(
        ("script", "num_expected"),
        (
            ("SELECT * FROM my_table;", 2),
            ("SELECT * FROM my_table; SELECT * FROM my_table;", 3),
        ),
    )
    def test_error_fewer_statements_than_expected(script, num_expected):
        with pytest.raises(NumberOfStatementsError):
            split_statements(script, num_expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("script", "num_expected"),
        (
            (
                """SELECT * FROM my_table; SELECT * FROM my_table;
                SELECT * FROM my_table;""",
                2,
            ),
            ("SELECT * FROM my_table;SELECT * FROM my_table;", 1),
        ),
    )
    def test_error_more_statements_than_expected(script, num_expected):
        with pytest.raises(NumberOfStatementsError):
            split_statements(script, num_expected)

    @staticmethod
    def test_correct_number_of_statements():
        script = "SELECT * FROM my_table; CREATE TABLE my_table;"

        actual = split_statements(script, 2)

        assert actual == ("SELECT * FROM my_table", "CREATE TABLE my_table")


class TestValidationStatementDefineProd:

    @staticmethod
    @pytest.mark.parametrize(
        "script",
        (
            "SELECT * FROM my_table;",
            "CREATE TABLE my_table;",
            "INSERT INTO my_table SELECT * FROM my_table;",
        ),
    )
    def test_invalid_create_prod_statement(script):
        with pytest.raises(InvalidStatementError):
            validate_create_statement_wh(script, "my_table")

    def test_valid_create_prod_statement(self):
        script = """CREATE TABLE IF NOT EXISTS my_table (
            my_column VARCHAR
            );"""
        actual = validate_create_statement_wh(script, "my_table")
        assert actual == script


class TestValidationStatementPopulateProd:

    @staticmethod
    @pytest.mark.parametrize(
        "script",
        (
            "SELECT * FROM my_table;",
            "CREATE TABLE my_table;",
            "CREATE TABLE IF NOT EXISTS my_table;",
        ),
    )
    def test_invalid_populate_prod_statement(script):
        with pytest.raises(InvalidStatementError):
            validate_populate_statement_wh(script, "my_table")


class TestValidationStatementDefineStaging:

    @staticmethod
    @pytest.mark.parametrize(
        "script",
        (
            "SELECT * FROM my_table;",
            "CREATE TABLE IF NOT EXISTS my_table;",
            "INSERT INTO my_table SELECT * FROM my_table;",
        ),
    )
    def test_invalid_create_staging_statement(script):
        with pytest.raises(InvalidStatementError):
            validate_create_staging_statement(script, "my_table")

    def test_valid_create_staging_statement(self):
        script = """CREATE TABLE my_table (
            my_column VARCHAR
            );"""
        actual = validate_create_staging_statement(script, "my_table")
        assert actual == script


class TestDependenciesDetection:

    TABLES = {"my_table", "other_table", "my_table_staging"}

    def test_depends_only_on_self(self):
        script = """INSERT INTO my_table SELECT 5 AS my_column;"""
        assert depends_on(script, self.TABLES) == {"my_table"}

    def test_dependency_on_from_clause(self):
        script = """INSERT INTO my_table SELECT * FROM other_table;"""
        assert depends_on(script, self.TABLES) == {
            "my_table",
            "other_table",
        }

    def test_dependency_on_join_clause(self):
        script = """INSERT INTO my_table SELECT * FROM my_table JOIN other_table;"""
        assert depends_on(script, self.TABLES) == {
            "my_table",
            "other_table",
        }

    def test_with_table_is_ignored(self):
        script = """WITH my_cte AS (SELECT * FROM other_table)
        INSERT INTO my_table SELECT * FROM my_cte;"""
        assert depends_on(script, self.TABLES) == {"my_table", "other_table"}

    def test_staging_table_does_not_match_non_staging_too(self):
        script = """SELECT * FROM my_table_staging;"""
        assert depends_on(script, self.TABLES) == {"my_table_staging"}


@pytest.mark.parametrize(
    ("statement", "expected_columns"),
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
        (  # Multiple columns ending with a FOREIGN KEY clause
            """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date,
                    FOREIGN KEY (note)
                );""",
            ("note", "date"),
        ),
        (  # Multiple columns ending with a REFERENCES clause
            """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date,
                    FOREIGN KEY (note)
                    REFERENCES other_table (note)
                );""",
            ("note", "date"),
        ),
        (  # Multiple columns ending with a ON UPDATE clause
            """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date,
                    FOREIGN KEY (note)
                    REFERENCES other_table (note)
                        ON UPDATE CASCADE
                );""",
            ("note", "date"),
        ),
        (  # Multiple columns ending with a ON DELETE clause
            """CREATE TABLE IF NOT EXISTS dm_table (
                    note,
                    date,
                    FOREIGN KEY (note)
                    REFERENCES other_table (note)
                        ON DELETE CASCADE
                );""",
            ("note", "date"),
        ),
    ),
)
def test_columns_inference(statement, expected_columns):
    columns = extract_attributes_from_create_statement(statement)
    assert columns == expected_columns


@pytest.mark.parametrize(
    ("staging_statement", "expected"),
    (
        (  # One column
            """CREATE TABLE dm_table_staging (
                a_note
            );""",
            """INSERT INTO dm_table_staging(a_note)
            VALUES(?)
            ON CONFLICT DO UPDATE
            SET
                a_note = excluded.a_note;
            """,
        ),
        (  # Multiple columns
            """CREATE TABLE dm_table_staging (
            a_note,
            a_date
            );""",
            """INSERT INTO dm_table_staging(a_note, a_date)
            VALUES(?, ?)
            ON CONFLICT DO UPDATE
            SET
                a_note = excluded.a_note,
                a_date = excluded.a_date;
            """,
        ),
    ),
)
def test_insert_values_into_staging_is_derived_from_staging_statement(
    staging_statement, expected
):
    actual = derive_populate_staging_statement(staging_statement, "dm_table_staging")
    assert strings_equivalent(actual, expected)


def test_drop_table_statement_is_generated():
    actual = derive_drop_table_statement("dm_table")
    expected = "DROP TABLE IF EXISTS dm_table;"
    assert actual == expected
