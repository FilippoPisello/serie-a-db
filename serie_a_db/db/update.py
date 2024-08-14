"""Logic to update the db."""

from datetime import datetime

from serie_a_db.db.client import Db
from serie_a_db.db.table import DbTable


class DbUpdater:
    """Entity to update the database."""

    def __init__(self, db: Db, schema: dict[str, DbTable]) -> None:
        """Initialize the builder.

        Args:
        ----
            db: The database client.
            schema: The schema of the database.

        """
        self.db = db
        self.schema = schema
        self.update_start_ts = datetime.now()

    def update_all_tables(self) -> None:
        """Update all tables in the schema."""
        self.update_tables(tables=self.schema)

    def update_tables(self, tables: dict[str, DbTable]) -> None:
        """Update the passed tables and their upstream dependencies.

        Args:
        ----
            tables: The tables to update.

        """
        for table in tables.values():
            self.update_table_and_upstream_dependencies(table)

    def update_table_and_upstream_dependencies(self, table: DbTable) -> None:
        """Update the passed table and its upstream dependencies."""
        for dependency in table.depends_on(self.schema):
            self.update_table_and_upstream_dependencies(self.schema[dependency])

        # Do not update if already updated at this runtime
        if self.db.meta.was_updated_since(table.name, self.update_start_ts):
            return

        table.update(self.db)
        self.db.meta.log_table_update(table.name)
