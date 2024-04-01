"""Custom exceptions."""

from pathlib import Path


class SetupError(ValueError):
    """Any error related to the user-provided setup/settings."""

    def __init__(self, message):
        super().__init__(message)


class QueryError(SetupError):
    """Any error related to the user-provided queries."""


class CreateStatementError(QueryError):
    """The query must contain a valid CREATE TABLE statement."""

    def __init__(self, query_path: Path) -> None:
        message = (
            f"Query '{query_path}' does not contain a valid CREATE TABLE statement."
        )
        super().__init__(message)


class InsertStatementError(QueryError):
    """If more then one statement is present, one must be an insert statement."""

    def __init__(self, query_path: Path) -> None:
        message = (
            f"Query '{query_path}' has more than one statement "
            "but none of them is an INSERT statement."
        )
        super().__init__(message)


class NumberOfStatementsError(QueryError):
    """The number of statements in the query must be 1 or 3+."""

    def __init__(self, query_path: Path, num_of_statements: int) -> None:
        message = (
            f"Query '{query_path}' must contain 1 or 3+ statements:"
            f"found {num_of_statements}."
        )
        super().__init__(message)


class ColumnsNotFoundError(QueryError):
    """The query must contain a valid CREATE TABLE statement."""

    def __init__(self, query_path: Path, query: str) -> None:
        message = (
            f"Could not find any columns for prod query in file {query_path}: "
            f"\n{query}"
        )
        super().__init__(message)


class TableUpdateError(Exception):
    """Any error related to the table update."""

    def __init__(self, table_name: str, specific_message: str) -> None:
        message = f"Error updating table '{table_name}': {specific_message}"
        super().__init__(message)


class IncompatibleDataError(TableUpdateError):
    """The data extracted from the source is incompatible with the table."""

    def __init__(self, table_name: str, expected_columns: tuple, data_columns: tuple):
        message = (
            "cannot insert data into the staging table. "
            f"Expected columns {expected_columns} but got {data_columns}."
        )
        super().__init__(table_name, message)


class BoundaryNotFoundError(TableUpdateError):
    """The boundary is not found in the dictionary."""

    def __init__(self, table_name: str, boundary: str, boundaries: dict):
        message = f"boundary '{boundary}' not found in the boundaries dictionary: {boundaries}."
        super().__init__(table_name, message)
