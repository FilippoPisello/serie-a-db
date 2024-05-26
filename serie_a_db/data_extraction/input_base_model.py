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

    @classmethod
    def fields(cls) -> tuple[str, ...]:
        """Return the fields of the model."""
        return tuple(cls.model_fields.keys())

    def assert_equal(self, other_model: BaseModel) -> None:
        """Assert that two models are equal.

        If not, return a detailed error message with the differences found.
        """
        this, other = self.model_dump(), other_model.model_dump()
        try:
            assert this == other
        except AssertionError as e:
            if this.keys() != other.keys():
                raise AssertionError(
                    f"Models have different keys: {this.keys()} vs {other.keys()}"
                ) from e
            differences = {k: (this[k], other[k]) for k in this if this[k] != other[k]}
            raise AssertionError(f"Models have different values: {differences}") from e
