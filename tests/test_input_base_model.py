import pytest
from pydantic import ValidationError

from serie_a_db.data_extraction.input_base_model import DbInputBaseModel


class DummyInput(DbInputBaseModel):
    name: str
    age: int


def test_validation_works_as_expected():
    """Pydantic validation still works as expected."""
    # expect no errors
    DummyInput(name="John", age=25)
    with pytest.raises(ValidationError):
        # expect an error
        DummyInput(name="John", age="non-a-number")


def test_fields_are_accessible_as_in_namedtuple():
    """Fields are accessible as in a namedtuple."""
    actual = DummyInput(name="John", age=25).to_namedtuple()._fields
    expected = ("name", "age")
    assert actual == expected


def test_values_are_accessible_as_in_namedtuple():
    """Values are accessible as in a namedtuple."""
    actual = DummyInput(name="John", age=25).to_namedtuple()
    expected = ("John", 25)
    assert actual == expected


def test_values_can_be_unpacked_as_in_namedtuple():
    """Values can be unpacked as in a namedtuple."""
    actual = DummyInput(name="John", age=25).to_namedtuple()
    name, age = actual
    assert name == actual.name
    assert age == actual.age
