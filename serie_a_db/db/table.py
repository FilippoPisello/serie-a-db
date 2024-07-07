"""Define the classes to represent the tables in the database."""

import csv
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, NamedTuple, Self

from serie_a_db import DEFINITIONS_DIR, context
from serie_a_db.db.client import Db
from serie_a_db.exceptions import IncompatibleDataError, NoSuchTableError
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

LOGGER = logging.getLogger(__name__)


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
        LOGGER.info("Updating table %s", self.name)
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
    def staging_attributes(self) -> tuple[str, ...]:
        """Attributes of the staging table."""
        return extract_attributes_from_create_statement(self.definition_statement)

    @property
    def drop_statement(self) -> str:
        """SQL statement to drop the staging table."""
        return derive_drop_table_statement(self.name)

    def update(self, db: Db) -> None:
        """Return the names of the tables this table depends on."""
        LOGGER.info("Updating table %s", self.name)

        if self._table_should_be_recreated(db):
            # Drop and recreate the staging table
            db.execute(self.drop_statement)
            db.execute(self.definition_statement)
            # Need to commit as extracting external data might rely on the table
            db.commit()

        data = self.extract_external_data()
        if not data:
            LOGGER.info("No data to load into %s", self.name)
            return

        try:
            self.error_if_data_incompatible(data, self.staging_attributes)
            # New data will always overwrite the existing data on conflict
            db.cursor.executemany(self.populate_statement, data)
            db.commit()
        except Exception as e:
            # If anything goes wrong, emergency save to local csv file
            LOGGER.error("Something went wrong. Saving data to CSV file...")
            self._save_to_csv(data)
            raise e

    def _table_should_be_recreated(self, db: Db) -> bool:
        """Check if the table should be recreated."""
        try:
            current_attributes = db.get_attributes(self.name)
        except NoSuchTableError:
            # Create the table if it doesn't exist
            return True

        # Recreate the table if the attributes have changed
        return current_attributes != self.staging_attributes

    @classmethod
    def error_if_data_incompatible(
        cls, data: list[NamedTuple], attributes: tuple[str, ...]
    ) -> None:
        """Check that the data is compatible with the table.

        Performing this check as we are generating programmatically the SQL
        query to insert the data into the staging table. We want to avoid
        loading data in the wrong place.
        """
        # Assuming that if the first and last records are valid, the rest
        # of the records are valid as well
        if data[0]._fields != attributes:
            raise IncompatibleDataError(attributes, data[0]._fields)
        if data[-1]._fields != attributes:
            raise IncompatibleDataError(attributes, data[-1]._fields)

    def _save_to_csv(self, data: list[NamedTuple]) -> None:
        """Save the data to a CSV file."""
        with open(
            f"recovery_{self.name}.csv", "w", encoding="utf-8", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(data[0]._fields)
            writer.writerows(data)


def read_script_from_file(table_name: str, directory: Path) -> str:
    """Read a SQL script from a file."""
    path = directory / f"{table_name}.sql"
    context.SCRIPT_BEING_PARSED = path
    return path.read_text()
