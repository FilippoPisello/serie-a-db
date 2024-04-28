"""Wrapper around sqlite3.db adding some utility methods."""

import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import Self

from serie_a_db import DB_FILE, META_DIR
from serie_a_db.utils import now


class Db:
    """Interface to the database."""

    def __init__(self, db_path: Path | str = DB_FILE) -> None:
        # MyPy is somehow unaware of the existence of autocommit
        self.db: Connection = connect(db_path, autocommit=False)  # type: ignore
        self.cursor: Cursor = self.db.cursor()
        self.meta = DbMeta(self)

    @classmethod
    def in_memory(cls) -> Self:
        """Create a Db instance in memory."""
        return cls(db_path=":memory:")

    def select(self, statement: str, *args, **kwargs) -> list[tuple] | list:
        """Return the results of a SELECT statement."""
        return self.execute(statement, *args, **kwargs).fetchall()

    def execute(self, statement: str, *args, **kwargs) -> Cursor:
        """Execute a statement."""
        try:
            return self.cursor.execute(statement, *args, **kwargs)
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(f"Error executing: {statement}") from e

    def close_connection(self) -> None:
        """Close the connection to the database."""
        self.db.close()

    def commit(self) -> None:
        """Commit the transaction."""
        self.db.commit()

    def count_rows(self, table_name: str) -> int:
        """Return the number of rows in the table."""
        return self.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

    def get_all_rows(self, table_name: str) -> list[tuple] | list:
        """Return all rows from the table."""
        return self.execute(f"SELECT * FROM {table_name}").fetchall()


class DbMeta:
    """Interface to the meta database."""

    def __init__(self, db: Db) -> None:
        self.db = db

    def create_meta_tables(self) -> None:
        """Create the meta tables if they don't exist."""
        for file in META_DIR.iterdir():
            self.db.execute(file.read_text())
        return self.db.commit()

    def log_table_update(self, table_name: str) -> None:
        """Log the update on the ft_tables_update."""
        n_rows = self.db.count_rows(table_name)

        self.db.execute(
            """
            INSERT INTO ft_tables_update(table_name, datetime_updated, rows_number)
            VALUES(?, ?, ?);
            """,
            (table_name, now().isoformat(sep=" ", timespec="milliseconds"), n_rows),
        )
