"""Generic classes for updating a database table."""

from abc import ABC, abstractmethod
from sqlite3 import Cursor

from serie_a_db.update.definitions_query_reading import DefinitionQuery
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
        query = self.read_definition_query()

        self.db.execute(query.create_prod_table)
        self.db.execute(query.create_staging_table)

        data = self.extract_data()
        self.populate_staging_table(data)
        self.db.execute(query.insert_from_staging_to_prod)

    def read_definition_query(self) -> DefinitionQuery:
        """Read the definition query from the file."""
        return DefinitionQuery.from_definitions(self.table_name())

    @abstractmethod
    def extract_data(self) -> list[tuple]:
        """Extract the data from the source."""

    def populate_staging_table(self, data: list[tuple]) -> None:
        """Populate the staging table."""
        # Look into using executemany
        raise NotImplementedError()
