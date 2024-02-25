import pytest

from serie_a_db.update import DefinitionQuery


class TestSingleQuerySpecified:

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
        assert DefinitionQuery(query=query, name="dm_table").staging == query.replace(
            "dm_table", "dm_table_staging"
        ).replace("IF NOT EXISTS", "")


class TestTwoQueries:

    def test_if_staging_and_actual_statement_are_swapped_then_error(self):
        """The non-staging table must have the IF NOT EXISTS clause."""
        query = """
        CREATE TABLE IF NOT EXISTS dm_table_staging (
            note
        );

        CREATE TABLE dm_table (
            note
        );
        """
        with pytest.raises(ValueError):
            DefinitionQuery(query=query, name="dm_table")


def strings_equivalent(str1: str, str2: str) -> bool:
    """Check if strings are equal after removing newlines and multiple spaces."""
    parsed_str1 = _strip_whitespaces_and_newlines(str1)
    parsed_str2 = _strip_whitespaces_and_newlines(str2)
    return parsed_str1 == parsed_str2


def _strip_whitespaces_and_newlines(string: str) -> str:
    return " ".join(string.split()).replace("\n", "")


@pytest.mark.parametrize(
    ("string1", "string2"),
    [
        ("lorem ipsum", "lorem  ipsum"),
        ("lorem ipsum", "lorem      ipsum"),
        ("lorem ipsum", "lorem ipsum"),
        ("lorem ipsum", "lorem\nipsum"),
    ],
)
def test_strings_equivalent(string1, string2):
    assert strings_equivalent(string1, string2)
