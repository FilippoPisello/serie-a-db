"""Custom exceptions."""

from sqlite3 import OperationalError

from serie_a_db import context


class SetupError(ValueError):
    """Any error related to the user-provided setup/settings."""

    def __init__(self, message):
        super().__init__(message)


class InvalidSqlScriptError(SetupError):
    """Any error related to the user-provided queries."""

    def __init__(self, specific_message: str) -> None:
        script = context.SCRIPT_BEING_PARSED
        message = f"Error with SQL script '{script}': {specific_message}"
        super().__init__(message)


class NumberOfStatementsError(InvalidSqlScriptError):
    """The script has a different number of statements than expected."""

    def __init__(self, expected: int, actual: int) -> None:
        msg = f"expected {expected} statements in the query, but found {actual}."
        super().__init__(msg)


class InvalidStatementError(InvalidSqlScriptError):
    """The statement does not match the expected format."""

    def __init__(self, missing_pattern: str) -> None:
        msg = f"statement missing the expected pattern: {missing_pattern}."
        super().__init__(msg)


class ColumnsNotFoundError(InvalidSqlScriptError):
    """Could not find any columns in the definition statement."""

    def __init__(self, statement: str) -> None:
        msg = f"could not find any columns in the definition statement: {statement}."
        super().__init__(msg)


class TableUpdateError(Exception):
    """Any error related to the table update."""

    def __init__(self, specific_message: str) -> None:
        table_name = context.TABLE_BEING_UPDATED
        message = f"Error updating table '{table_name}': {specific_message}"
        super().__init__(message)


class IncompatibleDataError(TableUpdateError):
    """The data extracted from the source is incompatible with the table."""

    def __init__(self, expected_columns: tuple, data_columns: tuple):
        msg = (
            "cannot insert data into the staging table. "
            f"Expected columns {expected_columns} but got {data_columns}."
        )
        super().__init__(msg)


class NoSuchTableError(OperationalError):
    """The table does not exist in the database."""

    def __init__(self) -> None:
        msg = "Trying to access a table that does not exist!"
        super().__init__(msg)


def raise_proper_operational_error(e: OperationalError) -> None:
    """Raise a proper exception for an OperationalError."""
    excinfo = str(e)
    if "no such table" in excinfo:
        raise NoSuchTableError() from e
    raise e
