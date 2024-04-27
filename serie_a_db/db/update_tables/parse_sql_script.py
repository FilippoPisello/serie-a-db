"""Generic classes for updating a database table."""

import re

from serie_a_db.exceptions import (
    ColumnsNotFoundError,
    InvalidStatementError,
    NumberOfStatementsError,
)
from serie_a_db.utils import split_no_empty, strip_whitespaces_and_newlines


def split_statements(script: str, num_expected: int) -> tuple[str, ...]:
    """Split a SQL script into statements.

    Raise an error if the number of found statements is different from the
    expected number.
    """
    statements = split_no_empty(script, ";")
    if len(statements) != num_expected:
        raise NumberOfStatementsError(num_expected, len(statements))
    return tuple(statements)


def validate_create_prod_statement(statement: str, table_name: str) -> str:
    """Validate the CREATE TABLE statement for the production table."""
    expected_pattern = f"CREATE TABLE IF NOT EXISTS {table_name} "
    if expected_pattern not in statement:
        raise InvalidStatementError(expected_pattern)
    return statement


def validate_populate_prod_statement(statement: str, table_name: str) -> str:
    """Validate the INSERT statement for populating the production table."""
    expected_pattern = f"INSERT INTO {table_name}"
    if expected_pattern not in statement:
        raise InvalidStatementError(expected_pattern)
    return statement


def validate_create_staging_statement(statement: str, table_name: str) -> str:
    """Validate the CREATE TABLE statement for the staging table."""
    expected_pattern = f"CREATE TABLE {table_name} "
    if expected_pattern not in statement:
        raise InvalidStatementError(expected_pattern)
    return statement


def depends_on(statement: str, all_tables: set[str]) -> set[str]:
    """Extract the tables that the statement depends on."""
    return {table for table in all_tables if table in statement}


def infer_populate_staging_statement(definition_statement: str, table_name: str) -> str:
    columns = extract_columns_from_create_statement(definition_statement)
    columns_str = ", ".join(columns)
    question_marks = ", ".join("?" for _ in columns)
    return f"""INSERT INTO {table_name}({columns_str})
        VALUES({question_marks});"""


def extract_columns_from_create_statement(create_statement: str) -> tuple[str]:
    """Extract the columns from a CREATE TABLE statement.

    It is assumed that each column is defined in a separate line.
    """
    # Matching anything between the first "(" and the last ")"
    try:
        # mypy does not understand the try-except construct
        re_match = re.search(r"\(([\S\s.]*)\)", create_statement).group(1)  # type: ignore
    except AttributeError as exc:
        raise ColumnsNotFoundError(create_statement) from exc

    # Split by newline to isolate the single column definitions
    col_definition_clauses = [
        strip_whitespaces_and_newlines(col)
        for col in re_match.split("\n")
        if strip_whitespaces_and_newlines(col)
    ]
    # Split by spaces to isolate the column name (from other stuff like
    # types, constraints, etc.)
    columns_and_ending_clauses = tuple(
        x[0].rstrip(",") for x in [col.split() for col in col_definition_clauses]
    )
    # Remove unwanted values like PRIMARY KEY, CHECK, etc.
    return tuple(
        col
        for col in columns_and_ending_clauses
        if col.upper() not in ("PRIMARY", "CHECK")
    )  # type: ignore # mypy thinks we might have a tuple of str | None
