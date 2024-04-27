from pathlib import Path
from typing import Callable, NamedTuple, Self

from serie_a_db import DEFINITIONS_DIR, context
from serie_a_db.db.db import Db
from serie_a_db.db.update_tables import TABLES
from serie_a_db.db.update_tables.parse_sql_script import (
    depends_on,
    extract_columns_from_create_statement,
    infer_populate_staging_statement,
    split_statements,
    validate_create_prod_statement,
    validate_create_staging_statement,
    validate_populate_prod_statement,
)
from serie_a_db.exceptions import IncompatibleDataError


class CoreTable:

    def __init__(
        self,
        name: str,
        statement_define_prod: str,
        statement_populate_prod: str,
    ) -> None:
        self.name = name
        self.statement_define_prod = statement_define_prod
        self.statement_populate_prod = statement_populate_prod

    @classmethod
    def from_file(cls, name: str, directory: Path = DEFINITIONS_DIR) -> Self:
        script = read_script_from_file(name, directory)
        statements = split_statements(script, num_expected=2)
        return cls(
            name,
            validate_create_prod_statement(statements[0], name),
            validate_populate_prod_statement(statements[1], name),
        )

    @property
    def depends_on(self) -> set[str]:
        all_tables = TABLES.keys()
        return depends_on(self.statement_populate_prod, all_tables) - {self.name}

    def update(self, db: Db) -> None:
        db.execute(self.statement_define_prod)
        db.execute(self.statement_populate_prod)


class StagingTable:

    def __init__(
        self,
        name: str,
        statement_define_staging: str,
        extract_external_data: Callable[[], list[NamedTuple]] | None,
    ) -> None:
        self.name = name
        self.statement_define_staging = statement_define_staging
        self.extract_external_data = extract_external_data

    @classmethod
    def from_file(
        cls,
        name: str,
        extract_external_data: Callable[[], list[NamedTuple]] | None,
        directory: Path = DEFINITIONS_DIR,
    ) -> Self:
        script = read_script_from_file(name, directory)
        statements = split_statements(script, num_expected=1)
        return cls(
            name,
            validate_create_staging_statement(statements[0], name),
            extract_external_data,
        )

    @property
    def depends_on(self) -> set[str]:
        return set()

    @property
    def statement_populate_staging(self) -> str:
        return infer_populate_staging_statement(
            self.statement_define_staging, self.name
        )

    @property
    def staging_columns(self) -> tuple[str]:
        return extract_columns_from_create_statement(self.statement_define_staging)

    def update(self, db: Db) -> None:
        db.execute(self.statement_define_staging)
        data = self.extract_external_data()

        self.error_if_data_incompatible(data, self.staging_columns)
        db.cursor.executemany(self.statement_populate_staging, data)

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
