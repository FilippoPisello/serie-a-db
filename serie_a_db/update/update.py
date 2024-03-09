"""Generic classes for updating a database table."""

from abc import ABC, abstractmethod
from sqlite3 import Cursor
from typing import Generator, NamedTuple

from serie_a_db.update.definitions_script_reading import DefinitionScript
from serie_a_db.utils import from_camel_to_snake_case


class DbTable(ABC):
    """Generic class for updating a database table."""

    def __init__(self, db: Cursor) -> None:
        self.db = db

    @classmethod
    def table_name(cls) -> str:
        """Return the name of the table."""
        return from_camel_to_snake_case(cls.__name__)

    @abstractmethod
    def update(self):
        """Update the table with the given data."""
        script = self.read_definition_script()

        self.db.execute(script.create_prod_table)
        self.db.execute(script.create_staging_table)

        data = self.extract_data()
        self.error_if_data_incompatible(data, script.staging_columns)
        self.populate_staging_table(data)
        self.db.execute(script.insert_from_staging_to_prod)

    def read_definition_script(self) -> DefinitionScript:
        """Read the definition script from the file."""
        return DefinitionScript.from_definitions(self.table_name())

    @abstractmethod
    def extract_data(self) -> list[NamedTuple]:
        """Extract the data from the source."""

    @staticmethod
    def error_if_data_incompatible(
        data: list[NamedTuple], columns: Generator[str, None, None]
    ) -> None:
        """Check that the data is compatible with the table.

        Performing this check as we are generating programmatically the SQL
        query to insert the data into the staging table. We want to avoid
        loading data in the wrong place.
        """
        # Assuming that if the first and last records are valid, the rest
        # of the records are valid as well
        first_record_is_invalid = data[0]._fields != tuple(columns)
        last_record_is_invalid = data[-1]._fields != tuple(columns)
        if first_record_is_invalid or last_record_is_invalid:
            raise ValueError("The data is not compatible with the table.")

    def populate_staging_table(self, data: list[NamedTuple]) -> None:
        """Populate the staging table."""
        # Look into using executemany
        raise NotImplementedError()
