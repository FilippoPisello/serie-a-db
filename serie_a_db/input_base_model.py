"""BaseModel for input data with conversion to namedtuple."""

from collections import namedtuple
from typing import NamedTuple

from pydantic import BaseModel


class DbInputBaseModel(BaseModel):
    """Model that extends pydantic's BaseModel to add conversion to namedtuple."""

    def to_namedtuple(self) -> NamedTuple:
        """Convert the model to a namedtuple."""
        dict_instance = self.model_dump()
        # Mypy complains about the string not being a string literal, but
        # the code works as expected. No evidence that this is a problem.
        blueprint = namedtuple(self.__class__.__name__, dict_instance.keys())  # type: ignore
        return blueprint(**dict_instance)
