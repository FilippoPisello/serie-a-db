"""Define the classes to represent the tables in the database."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, NamedTuple, Self

from serie_a_db import DEFINITIONS_DIR, context
from serie_a_db.db.client import Db
from serie_a_db.exceptions import IncompatibleDataError
from serie_a_db.sql_parsing import (
    depends_on,
    derive_drop_table_statement,
    derive_populate_staging_statement,
    extract_columns_from_create_statement,
    split_statements,
    validate_create_staging_statement,
    validate_create_statement_wh,
    validate_populate_statement_wh,
)


class DbTable(ABC):
    """Generic table in the database."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def depends_on(self, schema: dict[str, Self]) -> set[str]:
        """Return the names of the tables this table depends on."""

    @abstractmethod
    def update(self, db: Db) -> None:
        """Return the names of the tables this table depends on."""


class WarehouseTable(DbTable):
    """Table containing the data for the 'production' environment."""

    def __init__(
        self, name: str, definition_statement: str, populate_statement: str
    ) -> None:
        super().__init__(name)
        self.definition_statement = validate_create_statement_wh(
            definition_statement, name
        )
        self.populate_statement = validate_populate_statement_wh(
            populate_statement, name
        )

    @classmethod
    def from_file(cls, name: str, directory: Path = DEFINITIONS_DIR) -> Self:
        """Instantiate a WarehouseTable from a file."""
        script = read_script_from_file(name, directory)
        statements = split_statements(script, num_expected=2)
        return cls(
            name,
            validate_create_statement_wh(statements[0], name),
            validate_populate_statement_wh(statements[1], name),
        )

    def depends_on(self, schema: dict[str, Self]) -> set[str]:
        """Return the names of the tables this table depends on."""
        all_tables = set(schema.keys())
        return depends_on(self.populate_statement, all_tables) - {self.name}

    def update(self, db: Db) -> None:
        """Return the names of the tables this table depends on."""
        db.execute(self.definition_statement)
        db.execute(self.populate_statement)
        db.commit()


class StagingTable(DbTable):
    """Table containing data extracted from external sources.

    Staging tables are used to store data to serve as input for the warehouse
    tables.
    """

    def __init__(
        self,
        name: str,
        definition_statement: str,
        extract_external_data: Callable[[], list[NamedTuple]],
    ) -> None:
        super().__init__(name)
        self.definition_statement = definition_statement
        self.extract_external_data = extract_external_data

    @classmethod
    def from_file(
        cls,
        name: str,
        extract_external_data: Callable[[], list[NamedTuple]],
        directory: Path = DEFINITIONS_DIR,
    ) -> Self:
        """Instantiate a StagingTable from a file."""
        script = read_script_from_file(name, directory)
        statements = split_statements(script, num_expected=1)
        return cls(
            name,
            validate_create_staging_statement(statements[0], name),
            extract_external_data,
        )

    def depends_on(self, schema: dict[str, Self]) -> set[str]:  # noqa: ARG002
        """Return the names of the tables this table depends on."""
        return set()

    @property
    def populate_statement(self) -> str:
        """SQL statement to populate the staging table."""
        return derive_populate_staging_statement(self.definition_statement, self.name)

    @property
    def staging_columns(self) -> tuple[str, ...]:
        """Columns of the staging table."""
        return extract_columns_from_create_statement(self.definition_statement)

    @property
    def drop_statement(self) -> str:
        """SQL statement to drop the staging table."""
        return derive_drop_table_statement(self.name)

    def update(self, db: Db) -> None:
        """Return the names of the tables this table depends on."""
        # Drop and recreate the staging table
        db.execute(self.drop_statement)
        db.execute(self.definition_statement)
        data = self.extract_external_data()

        self.error_if_data_incompatible(data, self.staging_columns)
        db.cursor.executemany(self.populate_statement, data)
        db.commit()

    @classmethod
    def error_if_data_incompatible(
        cls, data: list[NamedTuple], columns: tuple[str, ...]
    ) -> None:
        """Check that the data is compatible with the table.

        Performing this check as we are generating programmatically the SQL
        query to insert the data into the staging table. We want to avoid
        loading data in the wrong place.
        """
        # Assuming that if the first and last records are valid, the rest
        # of the records are valid as well
        if data[0]._fields != columns:
            raise IncompatibleDataError(columns, data[0]._fields)
        if data[-1]._fields != columns:
            raise IncompatibleDataError(columns, data[-1]._fields)


def read_script_from_file(table_name: str, directory: Path) -> str:
    """Read a SQL script from a file."""
    path = directory / f"{table_name}.sql"
    context.SCRIPT_BEING_PARSED = path
    return path.read_text()
