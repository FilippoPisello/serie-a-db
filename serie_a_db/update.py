"""Generic classes for updating a database table."""

from abc import ABC, abstractmethod
from sqlite3 import Cursor
from typing import ClassVar, Self

from pydantic import BaseModel, model_validator

from serie_a_db import DEFINITIONS_DIR


class DbTable(ABC):
    """Generic class for updating a database table."""

    NAME = None

    def __init__(self, db: Cursor) -> None:
        self.db = db

    @abstractmethod
    def update(self, data):
        pass


class DefinitionQuery(BaseModel):
    query: str
    name: str
    DEFINITIONS_DIR: ClassVar[str] = DEFINITIONS_DIR

    @model_validator(mode="after")
    def check_query_is_create(self) -> None:
        """Validates that the query is a valid CREATE statement."""
        must_have = f"CREATE TABLE IF NOT EXISTS {self.name} "
        if must_have not in self.query:
            raise ValueError("Query must contain a valid CREATE TABLE statement.")
        return self

    @property
    def prod(self) -> str:
        """The production query."""
        return self.query

    @property
    def staging(self) -> str:
        """The staging query."""
        return self.query.replace(self.name, f"{self.name}_staging").replace(
            "IF NOT EXISTS", ""
        )

    @classmethod
    def from_file(cls, table_name: str) -> Self:
        """Creates a DefinitionQuery from a file."""
        return cls(query=cls.read_query_from_file(table_name), name=table_name)

    @classmethod
    def read_query_from_file(cls, table_name: str) -> str:
        """Reads a SQL query from a file."""
        return (cls.DEFINITIONS_DIR / f"{table_name}.sql").read_text()
