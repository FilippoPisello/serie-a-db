"""Generic classes for updating a database table."""

from abc import ABC, abstractmethod
from typing import NamedTuple, Self

from serie_a_db.db_setup import Db
from serie_a_db.update.definitions_script_reading import DefinitionScript
from serie_a_db.utils import from_camel_to_snake_case, now


class DbTable(ABC):
    """Generic class for updating a database table."""

    def __init__(self, db: Db, script: DefinitionScript) -> None:
        self.db = db
        self.script = script

    @classmethod
    def table_name(cls) -> str:
        """Return the name of the table."""
        return from_camel_to_snake_case(cls.__name__)

    @classmethod
    def from_definitions(cls, db: Db) -> Self:
        """Create a DbTable instance reading the matching script from definitions."""
        script = DefinitionScript.from_definitions(cls.table_name())
        return cls(db, script)

    @classmethod
    def from_string(cls, db: Db, script: str) -> Self:
        """Create a DbTable instance from a string."""
        return cls(db, DefinitionScript(script=script, name=cls.table_name()))

    def update(self) -> None:
        """Update the table with the given data."""
        self.db.execute(self.script.create_prod_table)
        self.db.execute(self.script.create_staging_table)

        data = self.extract_data()
        self.error_if_data_incompatible(data, tuple(self.script.staging_columns))
        self.populate_staging_table(data)
        self.db.execute(self.script.insert_from_staging_to_prod)

        self.log_update_in_meta_table()
        self.db.commit()

    @abstractmethod
    def extract_data(self) -> list[NamedTuple]:
        """Extract the data from the source."""

    @staticmethod
    def error_if_data_incompatible(
        data: list[NamedTuple], columns: tuple[str, ...]
    ) -> None:
        """Check that the data is compatible with the table.

        Performing this check as we are generating programmatically the SQL
        query to insert the data into the staging table. We want to avoid
        loading data in the wrong place.
        """
        # Assuming that if the first and last records are valid, the rest
        # of the records are valid as well
        first_record_is_invalid = data[0]._fields != columns
        last_record_is_invalid = data[-1]._fields != columns
        if first_record_is_invalid or last_record_is_invalid:
            raise ValueError("The data is not compatible with the table.")

    def populate_staging_table(self, data: list[NamedTuple]) -> None:
        """Populate the staging table."""
        self.db.cursor.executemany(self.script.insert_values_into_staging, data)

    def log_update_in_meta_table(self) -> None:
        """Log the update on the ft_tables_update."""
        n_rows = self.db.count_rows(self.table_name())

        self.db.execute(
            """
            INSERT INTO ft_tables_update(table_name, datetime_updated, rows_number)
            VALUES(?, ?, ?);
            """,
            (self.table_name(), now().strftime("%Y-%m-%d %H:%M:%S"), n_rows),
        )
