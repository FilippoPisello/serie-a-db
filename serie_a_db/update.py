"""Generic classes for updating a database table."""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from sqlite3 import Cursor
from typing import ClassVar, Self

from pydantic import BaseModel, model_validator

from serie_a_db import DEFINITIONS_DIR
from serie_a_db.exceptions import (
    ColumnsNotFoundError,
    CreateStatementError,
    InsertStatementError,
    NumberOfStatementsError,
)
from serie_a_db.utils import split_no_empty, strip_whitespaces_and_newlines


class DbTable(ABC):
    """Generic class for updating a database table."""

    NAME = None

    def __init__(self, db: Cursor) -> None:
        self.db = db

    @abstractmethod
    def update(self, data):
        """Update the table with the given data."""


class DefinitionQuery(BaseModel):
    """Represent a SQL query for creating a table."""

    query: str
    name: str
    DEFINITIONS_DIR: ClassVar[Path] = DEFINITIONS_DIR

    @model_validator(mode="after")
    def check_query(self) -> Self:
        """Validate that the sql file follows the expected format.

        Two options are allowed:
        - A single statement for creating the prod table.
        - 3+ statements for creating the prod table, creating the staging table,
            and inserting data into the prod table.

        In case of single statement, the other two properties are derived from
        it.
        """
        self._has_one_or_three_plus_statements()
        statements = split_no_empty(self.query, ";", maxplit=2)
        self._is_valid_create_statement(statements[0])
        if len(statements) > 1:
            self._is_valid_create_staging_statement(statements[1])
            self._contains_valid_insert_statement(statements[2:])
        return self

    def _has_one_or_three_plus_statements(self):
        number_of_statements = self.query.count(";")
        if number_of_statements != 1 and number_of_statements > 3:  # noqa: PLR2004
            raise NumberOfStatementsError(self.file_path, number_of_statements)

    def _is_valid_create_statement(self, statement: str) -> None:
        if f"CREATE TABLE IF NOT EXISTS {self.name} " not in statement:
            raise CreateStatementError(self.file_path)

    def _is_valid_create_staging_statement(self, statement: str) -> None:
        if f"CREATE TABLE {self.name}_staging " not in statement:
            raise CreateStatementError(self.file_path)

    def _contains_valid_insert_statement(self, statements: list[str]) -> None:
        insert_statements = ";\n".join(statements)
        if f"INSERT INTO {self.name}" not in insert_statements:
            raise InsertStatementError(self.file_path)

    @property
    def prod(self) -> str:
        """The production query."""
        return self._split_statements()[0]

    def _split_statements(self) -> tuple[str, str | None, str | None]:
        try:
            prod, staging, insert = split_no_empty(self.query, ";", maxplit=2)
            return prod + ";", staging + ";", insert
        except ValueError:
            return self.query, None, None

    @property
    def staging(self) -> str:
        """The staging query."""
        statement = self._split_statements()[1]
        # If the staging table is defined in the query, return it
        if statement:
            return statement
        # Otherwise, derive it from the prod table
        return self.prod.replace(self.name, f"{self.name}_staging").replace(
            "IF NOT EXISTS", ""
        )

    @property
    def insert(self) -> str:
        """The insert statement."""
        statement = self._split_statements()[2]
        # If the insert statement is defined in the query, return it
        if statement:
            return statement
        # Otherwise, derive it from the prod table
        columns_str = ", ".join(self._prod_columns())
        on_str = ", ".join(f"{col} = excluded.{col}" for col in self._prod_columns())
        return f"""
        INSERT INTO {self.name}
        SELECT {columns_str} FROM {self.name}_staging
        ON CONFLICT DO UPDATE
        SET {on_str};
        """

    def _prod_columns(self) -> list[str]:
        """Return the columns of the table."""
        re_match = re.search(r"\(([\S\s]*)\)", self.prod)
        if re_match is None:
            raise ColumnsNotFoundError(self.file_path, self.query)
        columns_text = re_match.group(1)
        columns_text = strip_whitespaces_and_newlines(columns_text).strip("()")
        return [x[0] for x in [col.split() for col in columns_text.split(",")]]

    @classmethod
    def from_definitions(cls, table_name: str) -> Self:
        """Create a DefinitionQuery from a file."""
        return cls(query=cls.read_query_from_file(table_name), name=table_name)

    @classmethod
    def read_query_from_file(cls, table_name: str) -> str:
        """Read a SQL query from a file."""
        return (cls.DEFINITIONS_DIR / f"{table_name}.sql").read_text()

    @property
    def file_path(self) -> Path:
        """The path to the file."""
        return self.DEFINITIONS_DIR / f"{self.name}.sql"
