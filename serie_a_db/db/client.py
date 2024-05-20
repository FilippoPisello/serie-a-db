"""Wrapper around sqlite3.db adding some utility methods."""

import sqlite3
from datetime import datetime
from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from time import sleep
from typing import Self

from serie_a_db import DB_FILE, META_DIR
from serie_a_db.exceptions import raise_proper_operational_error
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
            raise_proper_operational_error(e)

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
            statements = file.read_text().split(";")
            for statement in statements:
                self.db.execute(statement)
        return self.db.commit()

    def set_parameters(self, parameters: dict[str, float]) -> None:
        """Insert the parameters into the database."""
        self.db.cursor.executemany(
            """
            INSERT INTO dm_parameter(key, value)
            VALUES(?, ?);
            """,
            [(key, value) for key, value in parameters.items()],
        )
        return self.db.commit()

    def get_parameter(self, key: str) -> float:
        """Return the value of the parameter."""
        return self.db.execute(
            f"SELECT value FROM dm_parameter WHERE key = '{key}'"
        ).fetchone()[0]

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
        # Sleep for one millisecond to ensure that two updates cannot
        # be logged at the same time
        sleep(0.001)

    def was_updated_today(self, table_name: str) -> bool:
        """Return True if the table was updated today."""
        last_updated = self.last_updated(table_name)
        if last_updated is None:
            return False
        return last_updated.date() == now().date()

    def last_updated(self, table_name: str) -> None | datetime:
        """Return the timestamp for the last update of this table."""
        try:
            datetime_str = self.db.execute(
                f"""SELECT datetime_updated FROM ft_tables_update
                WHERE table_name = '{table_name}'
                ORDER BY datetime_updated DESC
                LIMIT 1"""
            ).fetchone()[0]
        except (IndexError, TypeError):
            return None
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
