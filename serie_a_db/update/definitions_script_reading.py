"""Generic classes for updating a database table."""

import re
from pathlib import Path
from typing import ClassVar, Generator, Self

from pydantic import BaseModel, model_validator

from serie_a_db import DEFINITIONS_DIR
from serie_a_db.exceptions import (
    ColumnsNotFoundError,
    CreateStatementError,
    InsertStatementError,
    NumberOfStatementsError,
)
from serie_a_db.utils import split_no_empty, strip_whitespaces_and_newlines


class DefinitionScript(BaseModel):
    """Represent a SQL script for creating an populating a table."""

    script: str
    name: str
    DEFINITIONS_DIR: ClassVar[Path] = DEFINITIONS_DIR

    @model_validator(mode="after")
    def check_script(self) -> Self:
        """Validate that the sql file follows the expected format.

        Two options are allowed:
        - A single statement for creating the prod table.
        - 3+ statements for creating the prod table, creating the staging table,
            and inserting data into the prod table.

        In case of single statement, the other two properties are derived from
        it.
        """
        self._has_one_or_three_plus_statements()
        statements = split_no_empty(self.script, ";", maxplit=2)
        self._is_valid_create_statement(statements[0])
        if len(statements) > 1:
            self._is_valid_create_staging_statement(statements[1])
            self._contains_valid_insert_statement(statements[2:])
        return self

    def _has_one_or_three_plus_statements(self):
        number_of_statements = self.script.count(";")
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

    @classmethod
    def from_definitions(cls, table_name: str) -> Self:
        """Create a DefinitionScript from a file."""
        return cls(script=cls.read_script_from_file(table_name), name=table_name)

    @property
    def create_prod_table(self) -> str:
        """The statement to create the production tables."""
        return self._split_statements()[0]

    @property
    def create_staging_table(self) -> str:
        """The statement to create the staging table."""
        statement = self._split_statements()[1]
        # If the staging table is defined in the script, return it
        if statement:
            return statement
        # Otherwise, derive it from the prod table
        return self.create_prod_table.replace(
            self.name, f"{self.name}_staging"
        ).replace("IF NOT EXISTS", "")

    @property
    def insert_from_staging_to_prod(self) -> str:
        """The insert statement to add data from the staging to the prod table."""
        statement = self._split_statements()[2]
        # If the insert statement is defined in the script, return it
        if statement:
            return statement
        # Otherwise, derive it from the prod table
        columns_str = ", ".join(self.prod_columns)
        on_str = ", ".join(f"{col} = excluded.{col}" for col in self.prod_columns)
        return f"""
        INSERT INTO {self.name}
        SELECT {columns_str} FROM {self.name}_staging
        WHERE true -- Disambiguates the following ON from potential JOIN ON
        ON CONFLICT DO UPDATE
        SET {on_str};
        """

    @property
    def insert_values_into_staging(self) -> str:
        """The insert values statement to populate the staging table."""
        columns_str = ", ".join(self.staging_columns)
        question_marks = ", ".join("?" for _ in self.staging_columns)
        return f"""INSERT INTO {self.name}_staging({columns_str})
        VALUES({question_marks});"""

    def _split_statements(self) -> tuple[str, str | None, str | None]:
        try:
            prod, staging, insert = split_no_empty(self.script, ";", maxplit=2)
            return prod + ";", staging + ";", insert
        except ValueError:
            return self.script, None, None

    @property
    def prod_columns(self) -> Generator[str, None, None]:
        """Return the columns of the table."""
        return self._extract_columns_from_create_statement(self.create_prod_table)

    @property
    def staging_columns(self) -> Generator[str, None, None]:
        """Return the columns of the staging table."""
        return self._extract_columns_from_create_statement(self.create_staging_table)

    def _extract_columns_from_create_statement(
        self, create_statement: str
    ) -> Generator[str, None, None]:
        re_match = re.search(r"\(([\S\s]*)\)", create_statement)
        if re_match is None:
            raise ColumnsNotFoundError(self.file_path, self.script)
        columns_text = strip_whitespaces_and_newlines(re_match.group(1)).strip("()")
        # Steps of the parsing:
        # Split by commas to isolate the single column definitions
        # Split by spaces to isolate the column name (from other stuff like
        # types, constraints, etc.)
        return (x[0] for x in [col.split() for col in columns_text.split(",")])

    @classmethod
    def read_script_from_file(cls, table_name: str) -> str:
        """Read a SQL script from a file."""
        return (cls.DEFINITIONS_DIR / f"{table_name}.sql").read_text()

    @property
    def file_path(self) -> Path:
        """The path to the file."""
        return self.DEFINITIONS_DIR / f"{self.name}.sql"
